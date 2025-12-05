"""Add os_type field to rules table

Revision ID: a3f279b92005
Revises: 72edc982a17e
Create Date: 2025-12-06 00:57:28.150834

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f279b92005'
down_revision: Union[str, Sequence[str], None] = '72edc982a17e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add os_type column to rules table
    op.add_column('rules', sa.Column('os_type', sa.String(length=20), nullable=True))
    
    # Update existing rules to set os_type based on agent_rule_id
    op.execute("""
        UPDATE rules 
        SET os_type = CASE 
            WHEN agent_rule_id LIKE 'UBU-%' THEN 'ubuntu'
            WHEN agent_rule_id LIKE 'WIN-%' THEN 'windows'
            ELSE NULL
        END
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove os_type column
    op.drop_column('rules', 'os_type')
