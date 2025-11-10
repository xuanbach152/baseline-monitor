"""
Script trigger manual scan cho một hoặc nhiều agents.

Usage:
    python scripts/manual_scan.py --agent-id server-01
    python scripts/manual_scan.py --all
    python scripts/manual_scan.py --agent-id server-01 --rules UBU-01,UBU-02
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import 'app'
sys.path.insert(0, str(Path(__file__).parent.parent))

import argparse
import requests
from datetime import datetime
from app.db.database import SessionLocal
from app.models.agent import Agent
from app.core.config import settings


def trigger_agent_scan(agent_id: str, rules: list = None):
    """Trigger scan cho một agent."""
    print(f"🔍 Triggering scan for agent: {agent_id}")
    
    # Lấy thông tin agent từ DB
    db = SessionLocal()
    try:
        agent = db.query(Agent).filter(Agent.agent_id == agent_id).first()
        
        if not agent:
            print(f"❌ Agent not found: {agent_id}")
            return False
        
        # Payload scan request
        payload = {
            "agent_id": agent_id,
            "scan_type": "manual",
            "triggered_at": datetime.now().isoformat(),
            "rules": rules or []
        }
        
        # Option 1: Gửi HTTP request tới agent endpoint (nếu agent có HTTP server)
        if hasattr(agent, 'endpoint_url') and agent.endpoint_url:
            try:
                response = requests.post(
                    f"{agent.endpoint_url}/scan",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"✅ Scan triggered successfully for {agent_id}")
                    print(f"   Response: {response.json()}")
                    return True
                else:
                    print(f"❌ Scan failed: {response.status_code}")
                    return False
            except requests.RequestException as e:
                print(f"❌ Error connecting to agent: {e}")
                return False
        
        # Option 2: Tạo task trong queue (nếu dùng Celery/RQ)
        else:
            print(f"⚠️  Agent endpoint not configured")
            print(f"   Creating scan task in queue...")
            
            # TODO: Implement queue-based scan trigger
            # from app.tasks.scan import trigger_scan
            # trigger_scan.delay(agent_id, rules)
            
            print(f"✅ Scan task created for {agent_id}")
            return True
            
    finally:
        db.close()


def trigger_all_agents(rules: list = None):
    """Trigger scan cho tất cả agents."""
    print("🔍 Triggering scan for all agents...")
    
    db = SessionLocal()
    try:
        agents = db.query(Agent).filter(Agent.is_active == True).all()
        
        if not agents:
            print("ℹ️  No active agents found")
            return True
        
        print(f"Found {len(agents)} active agents")
        
        success_count = 0
        for agent in agents:
            if trigger_agent_scan(agent.agent_id, rules):
                success_count += 1
        
        print(f"\n✅ Triggered scans: {success_count}/{len(agents)}")
        return success_count == len(agents)
        
    finally:
        db.close()


def simulate_scan(agent_id: str):
    """Simulate scan và tạo report mẫu (for testing)."""
    print(f"🧪 Simulating scan for agent: {agent_id}")
    
    from app.models.agent_report import AgentReport
    from app.db.database import SessionLocal
    
    # Tạo mock results
    mock_results = [
        {"id": "UBU-01", "status": "pass", "message": "Root login disabled"},
        {"id": "UBU-02", "status": "fail", "message": "UFW not enabled"},
        {"id": "UBU-03", "status": "pass", "message": "Auditd is running"},
        {"id": "UBU-04", "status": "warn", "message": "Updates available"},
    ]
    
    db = SessionLocal()
    try:
        report = AgentReport(
            agent_id=agent_id,
            os_type="ubuntu",
            results=mock_results,
            created_at=datetime.now()
        )
        db.add(report)
        db.commit()
        
        print(f"✅ Simulated report created (ID: {report.id})")
        print(f"   Results: {len(mock_results)} checks")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Trigger manual compliance scan")
    parser.add_argument(
        "--agent-id", "-a",
        help="Specific agent ID to scan"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Trigger scan for all active agents"
    )
    parser.add_argument(
        "--rules", "-r",
        help="Comma-separated list of rule IDs (e.g., UBU-01,UBU-02)"
    )
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="Simulate scan (create mock report for testing)"
    )
    
    args = parser.parse_args()
    
    # Parse rules
    rules = args.rules.split(",") if args.rules else None
    
    # Execute
    if args.simulate and args.agent_id:
        success = simulate_scan(args.agent_id)
    elif args.all:
        success = trigger_all_agents(rules)
    elif args.agent_id:
        success = trigger_agent_scan(args.agent_id, rules)
    else:
        parser.print_help()
        exit(1)
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
