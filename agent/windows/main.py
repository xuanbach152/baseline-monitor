#!/usr/bin/env python3
"""
Windows Agent Main Runner

Usage:
    python agent/windows/main.py
    
    # Hoặc chạy với custom config path
    python agent/windows/main.py --config C:\path\to\config.yaml
"""

import sys
import time
import signal
import argparse
import platform
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agent.common import (
    get_config,
    setup_logger,
    get_logger,
    BackendAPIClient,
    system_info
)
from agent.windows.scanner import run_scan
from agent.windows.violation_reporter import report_violations


class WindowsAgent:
    """Main Windows Agent class."""
    
    def __init__(self, config_path: str = "config.yaml"):
       
        self.config_path = config_path
        self.config = None
        self.client = None
        self.logger = None
        self.running = False
        self.agent_id = None
        
    def setup(self):
       
        print("=" * 60)
        print(" WINDOWS AGENT STARTING...")
        print("=" * 60)
        
     
        print(f"\n Loading config from: {self.config_path}")
        try:
            self.config = get_config(self.config_path)
            print(f"   Config loaded successfully")
            print(f"   Hostname: {self.config.hostname}")
            print(f"   OS Type: {self.config.os_type}")
            print(f"   Backend: {self.config.api_url}")
        except FileNotFoundError:
            print(f"    Config file not found: {self.config_path}")
            print(f"    Run setup script first:")
            print(f"      python agent/setup.py --backend-url http://backend:8000 --no-interactive")
            sys.exit(1)
        except Exception as e:
            print(f"    Failed to load config: {e}")
            sys.exit(1)
        
     
        print(f"\n Setting up logger...")
        try:
            self.logger = setup_logger(
                log_level=self.config.log_level,
                log_file=self.config.log_file,
                max_bytes=self.config.log_max_bytes,
                backup_count=self.config.log_backup_count,
                console_output=self.config.log_console_output
            )
            print(f"    Logger configured")
            print(f"    Log file: {self.config.log_file}")
            self.logger.info("=" * 60)
            self.logger.info("Windows Agent Starting")
            self.logger.info("=" * 60)
        except Exception as e:
            print(f"    Failed to setup logger: {e}")
            sys.exit(1)
        
        print(f"\n Creating API client...")
        try:
            self.client = BackendAPIClient(
                api_url=self.config.api_url,
                api_token=self.config.api_token,
                timeout=self.config.api_timeout,
                retry_attempts=self.config.api_retry_attempts
            )
            print(f"    API client created")
        except Exception as e:
            print(f"    Failed to create API client: {e}")
            self.logger.error(f"Failed to create API client: {e}")
            sys.exit(1)
    
    def check_backend_health(self) -> bool:
        
        print(f"\n Checking backend health...")
        self.logger.info("Checking backend health...")
        
        if self.client.health_check():
            print(f"    Backend is healthy")
            self.logger.info("Backend is healthy")
            return True
        else:
            print(f"    Backend is unreachable")
            self.logger.error("Backend is unreachable")
            return False
    
    def register_agent(self) -> bool:
       
        print(f"\n Agent Registration Flow")
        print("-" * 60)
        
    
        cached_agent_id = self.config.agent_id
        
        if cached_agent_id:
            print(f"    Found cached agent_id: {cached_agent_id}")
            print(f"    Using cached registration")
            self.logger.info(f"Using cached agent_id: {cached_agent_id}")
            self.agent_id = cached_agent_id
            return True
        

        print(f"    No cached agent_id found")
        print(f"    Starting auto-registration...")
        self.logger.info("No cached agent_id - starting auto-registration")
        

        print(f"\n    Collecting system information...")
        try:
            info = system_info.get_agent_info(include_system_stats=False)
            print(f"     • Hostname:    {info.get('hostname')}")
            print(f"     • IP Address:  {info.get('ip_address')}")
            print(f"     • OS:          {info.get('os')}")
            print(f"     • MAC Address: {info.get('mac_address')}")
            print(f"     • Version:     {info.get('version')}")
            self.logger.info(f"System info collected: {info}")
        except Exception as e:
            print(f"    Failed to collect system info: {e}")
            self.logger.error(f"Failed to collect system info: {e}")
            return False
        
        print(f"\n   Registering with backend...")
        print(f"     Endpoint: POST {self.config.api_url}/api/v1/agents")
        
        try:
            agent_id = self.client.register_agent(
                hostname=info['hostname'],
                ip_address=info.get('ip_address'),
                os=info.get('os'),
                version=info.get('version')
            )
            
            if agent_id:
                print(f"    Registration successful!")
                print(f"    Agent ID: {agent_id}")
                self.logger.info(f"Agent registered successfully with ID: {agent_id}")
                
              
                print(f"\n   Saving agent_id to cache...")
                self.config.save_agent_id(agent_id)
                print(f"     Cache file: .agent_cache.json")
                print(f"    Agent ID cached successfully")
                self.logger.info(f"Agent ID {agent_id} saved to cache")
                
                self.agent_id = agent_id
                return True
            else:
                print(f"    Registration failed - no agent_id returned")
                self.logger.error("Registration failed - no agent_id returned")
                return False
                
        except Exception as e:
            print(f"    Registration error: {e}")
            self.logger.error(f"Registration error: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
       
        if not self.agent_id:
            self.logger.warning("Cannot send heartbeat - no agent_id")
            return False
        
        try:
            success = self.client.send_heartbeat(self.agent_id)
            if success:
                self.logger.debug(f" Heartbeat sent successfully")
            else:
                self.logger.warning("Failed to send heartbeat")
            return success
        except Exception as e:
            self.logger.error(f"Heartbeat error: {e}")
            return False
    
    def run_scan_and_report(self):
        
        if not self.agent_id:
            self.logger.warning("Cannot run scan - no agent_id")
            return False
        
        try:
            self.logger.info("=" * 60)
            self.logger.info("🔍 Starting Windows compliance scan...")
            
        
            scan_result = run_scan(
                agent_id=self.agent_id,
                rules_path="agent/rules/windows_rules.json",
                timeout_per_rule=30
            )
            
      
            self.logger.info(f"Scan completed: {scan_result.compliance_rate:.1f}% compliance")
            self.logger.info(f"  Pass: {scan_result.pass_count}, Fail: {scan_result.fail_count}, Error: {scan_result.error_count}")
    
            if scan_result.fail_count > 0 or scan_result.error_count > 0:
                self.logger.info(" Reporting violations to backend...")
                report_success = report_violations(
                    client=self.client,
                    scan_result=scan_result,
                    report_pass=False  
                )
                
                if report_success:
                    self.logger.info(" Violations reported successfully")
                else:
                    self.logger.warning("  Some violations failed to report")
            else:
                self.logger.info(" No violations to report - system is compliant!")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Scan error: {e}", exc_info=True)
            return False
    
    def run(self):
       
        self.setup()
        
  
        if not self.check_backend_health():
            print(f"\nCannot start agent - backend is unreachable")
            print(f"  Please ensure backend is running at: {self.config.api_url}")
            sys.exit(1)
      
        if not self.register_agent():
            print(f"\nCannot start agent - registration failed")
            sys.exit(1)
        
  
        print(f"\n" + "=" * 60)
        print(f" AGENT STARTED SUCCESSFULLY")
        print(f"=" * 60)
        print(f"   Agent ID: {self.agent_id}")
        print(f"   Hostname: {self.config.hostname}")
        print(f"   Heartbeat interval: 60 seconds")
        print(f"   Scan interval: {self.config.scan_interval} seconds")
        print(f"\n   Press Ctrl+C to stop...")
        print("=" * 60)
        
        self.logger.info("Agent started successfully")
        self.logger.info(f"Agent ID: {self.agent_id}")
        self.logger.info("Starting main loop...")
        
        self.running = True
        heartbeat_interval = 60  # 60 seconds
        scan_interval = self.config.scan_interval 
        last_heartbeat = 0
        last_scan = 0
        
        self.logger.info("Running initial compliance scan...")
        self.run_scan_and_report()
        last_scan = time.time()
        
        try:
            while self.running:
                current_time = time.time()
                
                if current_time - last_heartbeat >= heartbeat_interval:
                    self.send_heartbeat()
                    last_heartbeat = current_time
                
                if current_time - last_scan >= scan_interval:
                    self.run_scan_and_report()
                    last_scan = current_time
                
                time.sleep(5)
                
        except KeyboardInterrupt:
            print(f"\n\n   Received shutdown signal...")
            self.logger.info("Received shutdown signal")
            self.shutdown()
        except Exception as e:
            print(f"\n\n Unexpected error: {e}")
            self.logger.error(f"Unexpected error: {e}", exc_info=True)
            self.shutdown()
            sys.exit(1)
    
    def shutdown(self):
        """Graceful shutdown."""
        print(f"\n Shutting down agent...")
        self.logger.info("Shutting down agent...")
       
        self.running = False
        
        print(f"    Agent stopped")
        self.logger.info("Agent stopped successfully")
        print("=" * 60)


def main():
    """Main entry point."""
    if platform.system() != "Windows":
        print("=" * 60)
        print("  WINDOWS AGENT")
        print("=" * 60)
        print(f"\nThis agent is designed for Windows only.")
        print(f"Current OS: {platform.system()}")
        print("\nFor Linux/Ubuntu, use: python agent/linux/main.py")
        print("=" * 60)
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Windows Agent for Baseline Monitor"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="Path to config file (default: config.yaml)"
    )
    
    args = parser.parse_args()
    
    agent = WindowsAgent(config_path=args.config)
    agent.run()


if __name__ == "__main__":
    main()
