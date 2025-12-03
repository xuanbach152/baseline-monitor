"""seed_cis_rules_ubuntu_and_windows

Revision ID: 72edc982a17e
Revises: 5da2cbb864f0
Create Date: 2025-12-03 16:54:04.567096

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table, column, String, Boolean, Integer


# revision identifiers, used by Alembic.
revision: str = '72edc982a17e'
down_revision: Union[str, Sequence[str], None] = '5da2cbb864f0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed CIS Benchmark rules for Ubuntu and Windows."""
    
    # Check if rules already exist to avoid duplicate key errors
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT COUNT(*) FROM rules WHERE agent_rule_id LIKE 'UBU-%' OR agent_rule_id LIKE 'WIN-%'"))
    existing_count = result.scalar()
    
    if existing_count > 0:
        print(f"⚠️  Found {existing_count} existing CIS rules, skipping seeding to avoid duplicates")
        return
    
    # Define rules table structure for bulk insert
    rules_table = table(
        'rules',
        column('name', String),
        column('description', String),
        column('check_expression', String),
        column('severity', String),
        column('category', String),
        column('active', Boolean),
        column('agent_rule_id', String),
    )
    
    # Ubuntu 20.04 LTS Rules (from agent/rules/ubuntu_rules.json)
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
    
    # Windows 10/11 Rules (from docs/selected_rules.md)
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
    
    # Combine all rules
    all_rules = ubuntu_rules + windows_rules
    
    # Bulk insert
    op.bulk_insert(rules_table, all_rules)
    
    print(f"✅ Seeded {len(ubuntu_rules)} Ubuntu rules and {len(windows_rules)} Windows rules")


def downgrade() -> None:
    """Remove seeded rules."""
    # Delete all rules with agent_rule_id starting with UBU- or WIN-
    op.execute(
        "DELETE FROM rules WHERE agent_rule_id LIKE 'UBU-%' OR agent_rule_id LIKE 'WIN-%'"
    )
