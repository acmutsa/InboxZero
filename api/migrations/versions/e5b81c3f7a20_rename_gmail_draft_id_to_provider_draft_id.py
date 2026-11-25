from typing import Sequence, Union

from alembic import op


revision: str = 'e5b81c3f7a20'
down_revision: Union[str, Sequence[str], None] = 'd7e2a9c41b58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('drafts', 'gmail_draft_id', new_column_name='provider_draft_id')


def downgrade() -> None:
    op.alter_column('drafts', 'provider_draft_id', new_column_name='gmail_draft_id')
