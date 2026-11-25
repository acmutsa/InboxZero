"""add gmail draft id to drafts

Revision ID: a4c9e7d1b2f3
Revises: 8b1f3c2d4e5a
Create Date: 2026-11-20 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4c9e7d1b2f3'
down_revision: Union[str, Sequence[str], None] = '8b1f3c2d4e5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('drafts', sa.Column('gmail_draft_id', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('drafts', 'gmail_draft_id')
