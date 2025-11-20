"""add_category_to_rules

Revision ID: 5da2cbb864f0
Revises: 3a860ae97000
Create Date: 2025-11-20 22:41:19.408747

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5da2cbb864f0'
down_revision: Union[str, Sequence[str], None] = '3a860ae97000'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add category column to rules table and update existing rules."""
    # Add category column
    op.add_column('rules', sa.Column('category', sa.String(50), nullable=True))
    
    # Update existing rules with category based on name
    op.execute("""
        UPDATE rules 
        SET category = CASE
            WHEN name LIKE '%SSH%' OR name LIKE '%ssh%' THEN 'SSH'
            WHEN name LIKE '%UFW%' OR name LIKE '%firewall%' OR name LIKE '%Firewall%' THEN 'Firewall'
            WHEN name LIKE '%audit%' OR name LIKE '%Audit%' THEN 'Auditing'
            WHEN name LIKE '%update%' OR name LIKE '%Update%' THEN 'System Updates'
            WHEN name LIKE '%password%' OR name LIKE '%Password%' THEN 'Password Policy'
            WHEN name LIKE '%tmp%' OR name LIKE '%mount%' THEN 'Filesystem'
            WHEN name LIKE '%AppArmor%' OR name LIKE '%SELinux%' THEN 'Access Control'
            WHEN name LIKE '%log%' OR name LIKE '%rsyslog%' THEN 'Logging'
            WHEN name LIKE '%IPv6%' OR name LIKE '%ipv6%' OR name LIKE '%network%' THEN 'Network'
            ELSE 'Security'
        END
        WHERE category IS NULL
    """)


def downgrade() -> None:
    """Remove category column from rules table."""
    op.drop_column('rules', 'category')
