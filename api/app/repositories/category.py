import uuid

from sqlalchemy.orm import Session
from app.constants import DEFAULT_CATEGORIES
from app.db.schema import Category


def create_default_categories(
    db: Session, 
    user_id: uuid.UUID
) -> list[Category]:
    categories = [Category(user_id=user_id, is_default=True, **category) for category in DEFAULT_CATEGORIES]
    db.add_all(categories)
    db.flush()
    return categories
