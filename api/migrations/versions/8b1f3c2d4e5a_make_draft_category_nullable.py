"""make drafts.category_id nullable

Revision ID: 8b1f3c2d4e5a
Revises: 576c87a78c87
Create Date: 2026-11-20 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8b1f3c2d4e5a'
down_revision: Union[str, Sequence[str], None] = '576c87a78c87'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # The pipeline drafts replies before emails are classified.
    op.alter_column('drafts', 'category_id', existing_type=sa.UUID(), nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Fails if any draft is still uncategorised (category_id IS NULL).
    op.alter_column('drafts', 'category_id', existing_type=sa.UUID(), nullable=False)
