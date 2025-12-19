"""
Script seed dữ liệu mẫu vào database.

Usage:
    python scripts/seed_data.py
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from app.core.config import settings
from app.modules.rules.models import Rule
from app.modules.agents.models import Agent

# Import violation model to resolve relationship
try:
    from app.modules.violations.models import Violation
except ImportError:
    pass

# Try to import user/auth models if they exist
try:
    from app.models.user import User
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    HAS_AUTH = True
except ImportError:
    HAS_AUTH = False
    pwd_context = None


def seed_users(db: Session):
    """Seed multiple users với các roles khác nhau."""
    if not HAS_AUTH:
        print(" Auth module not available, skipping user seeding")
        return
        
    print("  Seeding users...")
    
    users_data = [
        {"username": "admin", "email": "admin@baseline.local", 
         "password": "admin123", "role": "admin", "is_active": True},
        {"username": "operator", "email": "operator@baseline.local", 
         "password": "operator123", "role": "operator", "is_active": True},
        {"username": "viewer", "email": "viewer@baseline.local", 
         "password": "viewer123", "role": "viewer", "is_active": True},
    ]
    
    created_count = 0
    for user_data in users_data:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            db.add(User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=pwd_context.hash(user_data["password"]),
                role=user_data["role"],
                is_active=user_data["is_active"]
            ))
            created_count += 1
            print(f"  ✓ Created user: {user_data['username']} (role: {user_data['role']})")
    
    if created_count > 0:
        db.commit()
        print(f" Created {created_count} new users.")
    else:
        print("  - All users already exist.")


def seed_rules(db: Session):
    """Seed CIS Benchmark rules cho Ubuntu và Windows."""
    print(" Seeding CIS Benchmark rules...")
    
    # Ubuntu 20.04 LTS Rules
    ubuntu_rules = [
        {
            'agent_rule_id': 'UBU-01',
            'name': 'Disable root SSH login',
            'description': 'Prevent direct root login via SSH to reduce attack surface. Root access should only be obtained through sudo after regular user login.',
            'check_expression': "grep '^PermitRootLogin' /etc/ssh/sshd_config",
            'severity': 'high',
            'category': 'SSH',
            'active': True,
        },
        {
            'agent_rule_id': 'UBU-02',
            'name': 'Ensure UFW is enabled',
            'description': 'Enable Uncomplicated Firewall (UFW) to provide host-based firewall protection and control network traffic.',
            'check_expression': 'sudo ufw status',
            'severity': 'high',
            'category': 'Firewall',
            'active': True,
        },
        {
            'agent_rule_id': 'UBU-03',
            'name': 'Ensure auditd service is enabled',
            'description': 'Enable audit daemon (auditd) to track security-relevant events for compliance and forensic analysis.',
            'check_expression': 'systemctl is-enabled auditd',
            'severity': 'medium',
            'category': 'Auditing',
            'active': True,
        },
        {
            'agent_rule_id': 'UBU-04',
            'name': 'Ensure automatic updates are enabled',
            'description': 'Enable unattended-upgrades to automatically install security patches and keep the system up-to-date.',
            'check_expression': 'systemctl is-enabled unattended-upgrades',
            'severity': 'high',
            'category': 'System Updates',
            'active': True,
        },
        {
            'agent_rule_id': 'UBU-05',
            'name': 'Set password minimum length >= 14',
            'description': 'Enforce strong password policy by requiring minimum password length of 14 characters to resist brute-force attacks.',
            'check_expression': "grep '^PASS_MIN_LEN' /etc/login.defs",
            'severity': 'medium',
            'category': 'Password Policy',
            'active': True,
        },
        {
            'agent_rule_id': 'UBU-06',
            'name': 'Set password maximum age <= 90 days',
            'description': 'Enforce periodic password changes by setting maximum password age to 90 days or less.',
            'check_expression': "grep '^PASS_MAX_DAYS' /etc/login.defs",
            'severity': 'medium',
            'category': 'Password Policy',
            'active': True,
        },
        {
            'agent_rule_id': 'UBU-07',
            'name': 'Ensure /tmp has noexec option',
            'description': 'Prevent execution of binaries in /tmp directory to mitigate malware execution from temporary files.',
            'check_expression': 'findmnt -n /tmp | grep noexec',
            'severity': 'high',
            'category': 'Filesystem',
            'active': True,
        },
        {
            'agent_rule_id': 'UBU-08',
            'name': 'Ensure AppArmor is enabled',
            'description': 'Enable AppArmor for mandatory access control to confine programs and limit potential damage from security breaches.',
            'check_expression': "aa-status 2>/dev/null | grep -q 'apparmor module is loaded' && echo 'loaded' || echo 'not loaded'",
            'severity': 'high',
            'category': 'Access Control',
            'active': True,
        },
        {
            'agent_rule_id': 'UBU-09',
            'name': 'Ensure rsyslog service is enabled',
            'description': 'Enable rsyslog service to collect, process, and forward system log messages for monitoring and troubleshooting.',
            'check_expression': 'systemctl is-enabled rsyslog',
            'severity': 'medium',
            'category': 'Logging',
            'active': True,
        },
        {
            'agent_rule_id': 'UBU-10',
            'name': 'Disable IPv6 (if unused)',
            'description': 'Disable IPv6 protocol if not used to reduce attack surface and prevent IPv6-based attacks.',
            'check_expression': 'sysctl net.ipv6.conf.all.disable_ipv6',
            'severity': 'low',
            'category': 'Network',
            'active': True,
        },
    ]
    
    # Windows 10/11 Rules
    windows_rules = [
        {
            'agent_rule_id': 'WIN-01',
            'name': 'Disable SMBv1 protocol',
            'description': 'Disable legacy SMBv1 vulnerable protocol',
            'check_expression': 'Get-WindowsOptionalFeature -Online -FeatureName SMB1Protocol',
            'severity': 'high',
            'category': 'Network',
            'active': True,
        },
        {
            'agent_rule_id': 'WIN-02',
            'name': 'Ensure Windows Defender Antivirus is enabled',
            'description': 'Enable real-time protection',
            'check_expression': 'Get-MpComputerStatus | Select-Object AMServiceEnabled,AntispywareEnabled',
            'severity': 'critical',
            'category': 'Antivirus',
            'active': True,
        },
        {
            'agent_rule_id': 'WIN-03',
            'name': 'Ensure Firewall is enabled for all profiles',
            'description': 'Protect system from unauthorized access',
            'check_expression': 'Get-NetFirewallProfile | Select Name,Enabled',
            'severity': 'high',
            'category': 'Firewall',
            'active': True,
        },
        {
            'agent_rule_id': 'WIN-04',
            'name': 'Set Account lockout threshold <= 5',
            'description': 'Prevent brute-force login attempts',
            'check_expression': 'Get-AccountLockoutPolicy',
            'severity': 'medium',
            'category': 'Password Policy',
            'active': True,
        },
        {
            'agent_rule_id': 'WIN-05',
            'name': 'Set password minimum length >= 14',
            'description': 'Enforce strong password policy',
            'check_expression': 'net accounts',
            'severity': 'medium',
            'category': 'Password Policy',
            'active': True,
        },
        {
            'agent_rule_id': 'WIN-06',
            'name': 'Set password maximum age <= 90 days',
            'description': 'Require password change regularly',
            'check_expression': 'net accounts',
            'severity': 'medium',
            'category': 'Password Policy',
            'active': True,
        },
        {
            'agent_rule_id': 'WIN-07',
            'name': 'Enable User Account Control (UAC)',
            'description': 'Restrict silent privilege escalation',
            'check_expression': 'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System\\EnableLUA',
            'severity': 'high',
            'category': 'Access Control',
            'active': True,
        },
        {
            'agent_rule_id': 'WIN-08',
            'name': 'Enable Audit Logon Events',
            'description': 'Record logon/logoff attempts',
            'check_expression': 'auditpol /get /category:* | findstr "Logon"',
            'severity': 'medium',
            'category': 'Auditing',
            'active': True,
        },
        {
            'agent_rule_id': 'WIN-09',
            'name': 'Disable Remote Desktop (if unused)',
            'description': 'Reduce remote access attack surface',
            'check_expression': 'Get-ItemProperty -Path "HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server" -Name fDenyTSConnections',
            'severity': 'medium',
            'category': 'Network',
            'active': True,
        },
        {
            'agent_rule_id': 'WIN-10',
            'name': 'Ensure Automatic Updates are enabled',
            'description': 'Keep Windows up-to-date',
            'check_expression': 'Get-Service -Name wuauserv',
            'severity': 'high',
            'category': 'System Updates',
            'active': True,
        },
    ]
    
    all_rules = ubuntu_rules + windows_rules
    
    # Insert or update rules
    inserted_count = 0
    updated_count = 0
    for rule_data in all_rules:
        # Check if rule already exists
        existing = db.query(Rule).filter(Rule.agent_rule_id == rule_data['agent_rule_id']).first()
        if not existing:
            rule = Rule(**rule_data)
            db.add(rule)
            inserted_count += 1
            print(f"  ✓ Created {rule_data['agent_rule_id']}: {rule_data['name']}")
        else:
            # Update existing rule if check_expression is missing
            if not existing.check_expression:
                existing.check_expression = rule_data['check_expression']
                existing.name = rule_data['name']
                existing.description = rule_data['description']
                existing.severity = rule_data['severity']
                existing.category = rule_data['category']
                existing.active = rule_data['active']
                updated_count += 1
                print(f"  ↻ Updated {rule_data['agent_rule_id']}: {rule_data['name']}")
    
    if inserted_count > 0 or updated_count > 0:
        db.commit()
        if inserted_count > 0:
            print(f"\n✅ Inserted {inserted_count} new rules.")
        if updated_count > 0:
            print(f"✅ Updated {updated_count} existing rules.")
        
        # Summary
        ubuntu_count = db.query(Rule).filter(Rule.agent_rule_id.like('UBU-%')).count()
        windows_count = db.query(Rule).filter(Rule.agent_rule_id.like('WIN-%')).count()
        total_count = db.query(Rule).count()
        
        print(f"\n📊 Database Summary:")
        print(f"   Total rules: {total_count}")
        print(f"   Ubuntu rules: {ubuntu_count}")
        print(f"   Windows rules: {windows_count}")
    else:
        print("  - All rules are up to date.")


def seed_agents(db: Session):
    """Seed sample agents."""
    existing_count = db.query(Agent).count()
    
    if existing_count > 0:
        print(f" Agents already exist ({existing_count} agents in database).")
        return

    print("  Seeding sample agents...")
    
    agents = [
        Agent(
            hostname="web-server-01",
            ip_address="192.168.1.10",
            os="Ubuntu 22.04 LTS",
            version="1.0.0",
            is_online=True,
            last_seen=datetime.now()
        ),
        Agent(
            hostname="db-server-01",
            ip_address="192.168.1.11",
            os="Ubuntu 20.04 LTS",
            version="1.0.0",
            is_online=True,
            last_seen=datetime.now() - timedelta(minutes=5)
        ),
        Agent(
            hostname="win-desktop-01",
            ip_address="192.168.1.20",
            os="Windows 11 Pro",
            version="1.0.0",
            is_online=False,
            last_seen=datetime.now() - timedelta(hours=2)
        ),
    ]
    
    db.add_all(agents)
    db.commit()
    print(f" Seeded {len(agents)} agents successfully.")


def main():
    """Main entry point."""
    # Create database session
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        print("\n" + "="*70)
        print(" SEEDING DATABASE WITH SAMPLE DATA")
        print("="*70 + "\n")
        
        seed_users(db)
        print()
        seed_rules(db)
        print()
        seed_agents(db)
        
        print("\n" + "="*70)
        print(" ALL SEED DATA COMPLETED SUCCESSFULLY!")
        print("="*70)
        
        if HAS_AUTH:
            print("\n Default credentials:")
            print("  Admin:    username=admin    password=admin123")
            print("  Operator: username=operator password=operator123")
            print("  Viewer:   username=viewer   password=viewer123")
        
        print()
    except Exception as e:
        print(f"\n Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
