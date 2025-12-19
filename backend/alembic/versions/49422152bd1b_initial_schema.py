"""initial_schema

Revision ID: 49422152bd1b
Revises: 
Create Date: 2025-12-10 11:51:16.103007

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49422152bd1b'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create agents table
    op.create_table('agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('hostname', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('os', sa.String(length=100), nullable=True),
        sa.Column('version', sa.String(length=50), nullable=True),
        sa.Column('is_online', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('last_checkin', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('compliance_rate', sa.Float(), nullable=True, server_default='0.0'),
        sa.Column('last_scan_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_heartbeat', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_agents_hostname'), 'agents', ['hostname'], unique=False)
    op.create_index(op.f('ix_agents_id'), 'agents', ['id'], unique=False)
    
    # Create rules table
    op.create_table('rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('check_expression', sa.String(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True, server_default='medium'),
        sa.Column('category', sa.String(length=50), nullable=True),
        sa.Column('os_type', sa.String(length=20), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('agent_rule_id', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rules_agent_rule_id'), 'rules', ['agent_rule_id'], unique=True)
    op.create_index(op.f('ix_rules_id'), 'rules', ['id'], unique=False)
    
    # Create violations table
    op.create_table('violations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.Integer(), nullable=False),
        sa.Column('rule_id', sa.Integer(), nullable=False),
        sa.Column('detected_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('message', sa.String(), nullable=True),
        sa.Column('confidence_score', sa.Float(), nullable=True, server_default='1.0'),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_by', sa.String(length=100), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['rule_id'], ['rules.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_violations_agent_id'), 'violations', ['agent_id'], unique=False)
    op.create_index(op.f('ix_violations_detected_at'), 'violations', ['detected_at'], unique=False)
    op.create_index(op.f('ix_violations_id'), 'violations', ['id'], unique=False)
    op.create_index(op.f('ix_violations_rule_id'), 'violations', ['rule_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_violations_rule_id'), table_name='violations')
    op.drop_index(op.f('ix_violations_id'), table_name='violations')
    op.drop_index(op.f('ix_violations_detected_at'), table_name='violations')
    op.drop_index(op.f('ix_violations_agent_id'), table_name='violations')
    op.drop_table('violations')
    
    op.drop_index(op.f('ix_rules_id'), table_name='rules')
    op.drop_index(op.f('ix_rules_agent_rule_id'), table_name='rules')
    op.drop_table('rules')
    
    op.drop_index(op.f('ix_agents_id'), table_name='agents')
    op.drop_index(op.f('ix_agents_hostname'), table_name='agents')
    op.drop_table('agents')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
