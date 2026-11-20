import uuid

from sqlalchemy import func
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.schema import Category
from app.db.schema import Draft
from app.db.schema import Email


def email_counts_by_category(
    db: Session,
    email_account_id: uuid.UUID,
) -> list[dict]:
    rows = db.execute(
        select(
            Category.category_name,
            func.count(Email.id),
        )
        .join(Email, Email.category_id == Category.id)
        .where(Email.email_account_id == email_account_id)
        .group_by(Category.category_name)
    )

    return [
        {
            "category": category_name,
            "count": count,
        }
        for category_name, count in rows
    ]


def draft_count(
    db: Session,
    email_account_id: uuid.UUID,
) -> int:
    return db.scalar(
        select(func.count(Draft.id))
        .where(
            Draft.email_account_id == email_account_id,
            Draft.status == "in_review",
        )
    ) or 0
