from typing import Sequence, Union

from alembic import op


revision: str = 'd7e2a9c41b58'
down_revision: Union[str, Sequence[str], None] = 'a4c9e7d1b2f3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('emails', 'gmail_message_id', new_column_name='provider_message_id')
    op.execute(
        'ALTER TABLE emails RENAME CONSTRAINT uq_emails_email_account_id_gmail_message_id '
        'TO uq_emails_email_account_id_provider_message_id'
    )


def downgrade() -> None:
    op.execute(
        'ALTER TABLE emails RENAME CONSTRAINT uq_emails_email_account_id_provider_message_id '
        'TO uq_emails_email_account_id_gmail_message_id'
    )
    op.alter_column('emails', 'provider_message_id', new_column_name='gmail_message_id')
