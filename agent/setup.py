#!/usr/bin/env python3
"""
Agent Setup Script
==================
Script tự động cấu hình agent dựa trên thông tin hệ thống.

Luồng:
1. Thu thập system info tự động (hostname, OS, IP, MAC)
2. Hỏi user nhập backend URL
3. Tự động generate config.yaml phù hợp với máy này
4. Test kết nối với backend
5. Sẵn sàng chạy agent

Usage:
    python3 agent/setup.py
    
    # Hoặc non-interactive mode (dùng cho automation)
    python3 agent/setup.py --backend-url http://backend:8000 --no-interactive
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.common import system_info
import yaml


class AgentSetup:
    """Agent setup wizard."""
    
    def __init__(self, interactive=True):
        self.interactive = interactive
        self.config_path = Path("config.yaml")
        self.system_info = None
        self.config_data = {}
        
    def print_banner(self):
        """Print welcome banner."""
        print("\n" + "=" * 70)
        print("🚀 BASELINE MONITOR - AGENT SETUP WIZARD")
        print("=" * 70)
        print("\nThis wizard will:")
        print("  1. Auto-detect system information")
        print("  2. Configure connection to backend server")
        print("  3. Generate config.yaml for this machine")
        print("  4. Test connection")
        print("\n" + "=" * 70 + "\n")
    
    def collect_system_info(self):
        """Collect system information automatically."""
        print("📊 STEP 1: Collecting System Information")
        print("-" * 70)
        
        try:
            self.system_info = system_info.get_agent_info(include_system_stats=True)
            
            print(f"\n✅ System information collected:")
            print(f"   • Hostname:        {self.system_info['hostname']}")
            print(f"   • IP Address:      {self.system_info['ip_address']}")
            print(f"   • OS:              {self.system_info['os']}")
            print(f"   • MAC Address:     {self.system_info['mac_address']}")
            
            if 'public_ip' in self.system_info:
                print(f"   • Public IP:       {self.system_info.get('public_ip')}")
            
            if 'cpu' in self.system_info:
                cpu = self.system_info['cpu']
                print(f"   • CPU:             {cpu.get('logical_cores')} cores")
            
            if 'memory' in self.system_info:
                mem = self.system_info['memory']
                print(f"   • Memory:          {mem.get('total_gb')} GB")
            
            print("\n")
            return True
            
        except Exception as e:
            print(f"\n❌ Error collecting system info: {e}")
            return False
    
    def get_backend_config(self):
        """Get backend configuration from user."""
        print("🌐 STEP 2: Backend Server Configuration")
        print("-" * 70)
        
        if self.interactive:
            print("\nEnter the backend server URL:")
            print("  Example: http://192.168.1.100:8000")
            print("           https://baseline-monitor.company.com")
            
            while True:
                backend_url = input("\n Backend URL: ").strip()
                
                if not backend_url:
                    print("   ⚠️  Backend URL is required!")
                    continue
                
                if not (backend_url.startswith('http://') or backend_url.startswith('https://')):
                    print("   ⚠️  URL must start with http:// or https://")
                    continue
                
                break
            
            print("\nAPI Token (optional - press Enter to skip):")
            print("  • If backend requires authentication, enter JWT token")
            print("  • If no auth needed, just press Enter")
            print("  • You can also set AGENT_API_TOKEN environment variable later")
            
            api_token = input("\n API Token: ").strip()
            
        else:
            # Non-interactive mode - use default or environment
            backend_url = os.getenv('AGENT_BACKEND_URL', 'http://localhost:8000')
            api_token = os.getenv('AGENT_API_TOKEN', '')
            print(f"\n   Backend URL: {backend_url}")
            if api_token:
                print(f"   API Token:   {'*' * 20}")
            else:
                print(f"   API Token:   (not set)")
        
        self.config_data['backend'] = {
            'api_url': backend_url,
            'api_token': api_token,
            'timeout': 30,
            'retry_attempts': 3
        }
        
        print("\n✅ Backend configuration saved\n")
        return True
    
    def get_scanner_config(self):
        """Get scanner configuration."""
        print("🔍 STEP 3: Scanner Configuration")
        print("-" * 70)
        
        # Auto-detect OS type
        os_str = self.system_info['os'].lower()
        if 'ubuntu' in os_str or 'debian' in os_str:
            os_type = 'ubuntu'
            rules_path = './agent/rules/ubuntu_rules.json'
        elif 'windows' in os_str:
            os_type = 'windows'
            rules_path = './agent/rules/windows_rules.json'
        else:
            os_type = 'ubuntu'  # Default
            rules_path = './agent/rules/ubuntu_rules.json'
        
        print(f"\n✅ Auto-detected OS type: {os_type}")
        print(f"   Rules file: {rules_path}")
        
        if self.interactive:
            print("\nScan interval (in seconds):")
            print("  • 300  = 5 minutes")
            print("  • 1800 = 30 minutes")
            print("  • 3600 = 1 hour (recommended)")
            
            while True:
                interval_input = input("\n Scan interval [3600]: ").strip()
                
                if not interval_input:
                    scan_interval = 3600
                    break
                
                try:
                    scan_interval = int(interval_input)
                    if scan_interval < 60:
                        print("   ⚠️  Interval should be at least 60 seconds")
                        continue
                    break
                except ValueError:
                    print("   ⚠️  Please enter a valid number")
                    continue
        else:
            scan_interval = int(os.getenv('AGENT_SCAN_INTERVAL', '3600'))
        
        # Generate hostname for display
        hostname = self.system_info['hostname']
        # Shorten if too long
        if len(hostname) > 50:
            display_name = hostname[:47] + "..."
        else:
            display_name = hostname
        
        self.config_data['agent'] = {
            'hostname': hostname,
            'name': display_name,
            'os_type': os_type
        }
        
        self.config_data['scanner'] = {
            'scan_interval': scan_interval,
            'rules_path': rules_path,
            'command_timeout': 10,
            'report_pass_results': False
        }
        
        self.config_data['logging'] = {
            'level': 'INFO',
            'log_file': './logs/agent.log',
            'max_bytes': 10485760,  # 10MB
            'backup_count': 5,
            'console_output': True
        }
        
        print(f"   Scan interval: {scan_interval} seconds")
        print("\n✅ Scanner configuration saved\n")
        return True
    
    def generate_config_file(self):
        """Generate config.yaml file."""
        print("💾 STEP 4: Generating Configuration File")
        print("-" * 70)
        
        if self.config_path.exists():
            if self.interactive:
                print(f"\n⚠️  File {self.config_path} already exists!")
                response = input("   Overwrite? (yes/no) [no]: ").strip().lower()
                
                if response not in ['yes', 'y']:
                    print("\n❌ Setup cancelled. Existing config preserved.")
                    return False
            else:
                # Backup existing config
                backup_path = self.config_path.with_suffix('.yaml.backup')
                self.config_path.rename(backup_path)
                print(f"\n   Existing config backed up to: {backup_path}")
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write("# Generated by Agent Setup Wizard\n")
                f.write(f"# Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Hostname: {self.system_info['hostname']}\n")
                f.write("\n")
                yaml.dump(self.config_data, f, default_flow_style=False, sort_keys=False)
            
            print(f"\n✅ Configuration file created: {self.config_path}")
            print("\n📄 Configuration summary:")
            print(f"   • Agent hostname:  {self.config_data['agent']['hostname']}")
            print(f"   • OS type:         {self.config_data['agent']['os_type']}")
            print(f"   • Backend URL:     {self.config_data['backend']['api_url']}")
            print(f"   • Scan interval:   {self.config_data['scanner']['scan_interval']}s")
            print(f"   • Log file:        {self.config_data['logging']['log_file']}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error creating config file: {e}")
            return False
    
    def test_connection(self):
        """Test connection to backend."""
        print("\n🔌 STEP 5: Testing Backend Connection")
        print("-" * 70)
        
        try:
            from agent.common.http_client import BackendAPIClient
            
            client = BackendAPIClient(
                api_url=self.config_data['backend']['api_url'],
                api_token=self.config_data['backend']['api_token'],
                timeout=10,
                retry_attempts=1
            )
            
            print("\n   Connecting to backend...")
            
            if client.health_check():
                print("   ✅ Backend is reachable and healthy!")
                return True
            else:
                print("   ⚠️  Backend is unreachable")
                print("\n   This is OK - you can start backend later.")
                print("   Agent will auto-register when backend is available.")
                return True
                
        except Exception as e:
            print(f"   ⚠️  Connection test failed: {e}")
            print("\n   This is OK - you can start backend later.")
            return True
    
    def print_next_steps(self):
        """Print next steps."""
        print("\n" + "=" * 70)
        print("🎉 SETUP COMPLETE!")
        print("=" * 70)
        
        print("\n📋 Next steps:\n")
        
        print("1. Start the backend server (if not running):")
        print("   cd backend")
        print("   source venv/bin/activate")
        print("   uvicorn app.main:app --reload\n")
        
        print("2. Start the agent:")
        print("   python3 agent/linux/main.py\n")
        
        print("3. View logs:")
        print("   tail -f logs/agent.log\n")
        
        print("4. Check agent status in backend:")
        backend_url = self.config_data['backend']['api_url']
        print(f"   {backend_url}/api/v1/agents\n")
        
        print("=" * 70)
        print("\n✅ Agent is ready to run!\n")
    
    def run(self):
        """Run the setup wizard."""
        self.print_banner()
        
        # Step 1: Collect system info
        if not self.collect_system_info():
            return False
        
        # Step 2: Get backend config
        if not self.get_backend_config():
            return False
        
        # Step 3: Get scanner config
        if not self.get_scanner_config():
            return False
        
        # Step 4: Generate config file
        if not self.generate_config_file():
            return False
        
        # Step 5: Test connection
        self.test_connection()
        
        # Done
        self.print_next_steps()
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Agent Setup Wizard - Auto-configure agent for this machine"
    )
    parser.add_argument(
        '--backend-url',
        type=str,
        help='Backend URL (non-interactive mode)'
    )
    parser.add_argument(
        '--api-token',
        type=str,
        help='API token (non-interactive mode)'
    )
    parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Non-interactive mode (use env vars or defaults)'
    )
    
    args = parser.parse_args()
    
    # Set env vars if provided
    if args.backend_url:
        os.environ['AGENT_BACKEND_URL'] = args.backend_url
    
    if args.api_token:
        os.environ['AGENT_API_TOKEN'] = args.api_token
    
    # Run setup
    setup = AgentSetup(interactive=not args.no_interactive)
    
    try:
        success = setup.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
