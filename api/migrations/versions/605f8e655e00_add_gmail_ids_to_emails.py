"""add gmail message id to emails

Revision ID: 605f8e655e00
Revises: 2e726b713561
Create Date: 2026-11-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '605f8e655e00'
down_revision: Union[str, Sequence[str], None] = '2e726b713561'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('emails', sa.Column('gmail_message_id', sa.Text(), nullable=True))
    op.create_unique_constraint(
        'uq_emails_email_account_id_gmail_message_id',
        'emails',
        ['email_account_id', 'gmail_message_id'],
    )
    # Emails are saved before the pipeline classifies them.
    op.alter_column('emails', 'category_id', existing_type=sa.UUID(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Fails if any email is still unclassified (category_id IS NULL).
    op.alter_column('emails', 'category_id', existing_type=sa.UUID(), nullable=False)
    op.drop_constraint('uq_emails_email_account_id_gmail_message_id', 'emails', type_='unique')
    op.drop_column('emails', 'gmail_message_id')
