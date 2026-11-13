"""add gmail push columns to email accounts

Revision ID: 2e726b713561
Revises: c312f80aacd5
Create Date: 2026-11-13 11:42:32.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e726b713561'
down_revision: Union[str, Sequence[str], None] = 'c312f80aacd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('email_accounts', sa.Column('gmail_history_id', sa.Text(), nullable=True))
    op.add_column('email_accounts', sa.Column('gmail_watch_expires_at', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('email_accounts', 'gmail_watch_expires_at')
    op.drop_column('email_accounts', 'gmail_history_id')
