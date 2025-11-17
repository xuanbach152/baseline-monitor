"""add_agent_rule_id_to_rules

Revision ID: 3a860ae97000
Revises: f620c806eaee
Create Date: 2025-11-17 23:38:39.472791

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a860ae97000'
down_revision: Union[str, Sequence[str], None] = 'f620c806eaee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add agent_rule_id column to rules table
    op.add_column('rules', sa.Column('agent_rule_id', sa.String(length=20), nullable=True))
    op.create_index(op.f('ix_rules_agent_rule_id'), 'rules', ['agent_rule_id'], unique=True)
    
    # Seed 10 Ubuntu CIS rules
    op.execute("""
        INSERT INTO rules (name, description, severity, active, agent_rule_id) VALUES
        ('Disable root SSH login', 'Prevent direct root login via SSH to reduce attack surface', 'high', true, 'UBU-01'),
        ('Ensure UFW is enabled', 'Enable Uncomplicated Firewall (UFW) to provide host-based firewall protection', 'high', true, 'UBU-02'),
        ('Ensure auditd service is enabled', 'Enable audit daemon (auditd) to track security-relevant events', 'medium', true, 'UBU-03'),
        ('Ensure automatic updates are enabled', 'Enable unattended-upgrades to automatically install security patches', 'high', true, 'UBU-04'),
        ('Set password minimum length >= 14', 'Enforce strong password policy by requiring minimum password length of 14 characters', 'medium', true, 'UBU-05'),
        ('Set password maximum age <= 90 days', 'Enforce periodic password changes by setting maximum password age to 90 days or less', 'medium', true, 'UBU-06'),
        ('Ensure /tmp has noexec option', 'Prevent execution of binaries in /tmp directory to mitigate malware execution', 'high', true, 'UBU-07'),
        ('Ensure AppArmor is enabled', 'Enable AppArmor for mandatory access control to confine programs', 'high', true, 'UBU-08'),
        ('Ensure rsyslog service is enabled', 'Enable rsyslog service to collect, process, and forward system log messages', 'medium', true, 'UBU-09'),
        ('Disable IPv6 (if unused)', 'Disable IPv6 protocol if not used to reduce attack surface', 'low', true, 'UBU-10')
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove seeded rules
    op.execute("DELETE FROM rules WHERE agent_rule_id LIKE 'UBU-%';")
    
    # Drop index and column
    op.drop_index(op.f('ix_rules_agent_rule_id'), table_name='rules')
    op.drop_column('rules', 'agent_rule_id')
