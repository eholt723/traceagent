"""add client_info to runs

Revision ID: bbea5d7c2ff7
Revises: 5ad6fe52a6b9
Create Date: 2026-03-17 16:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bbea5d7c2ff7'
down_revision: Union[str, Sequence[str], None] = '5ad6fe52a6b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add client_info (TEXT, nullable) to runs table."""
    op.add_column('runs', sa.Column('client_info', sa.Text(), nullable=True))


def downgrade() -> None:
    """Remove client_info from runs table."""
    op.drop_column('runs', 'client_info')
