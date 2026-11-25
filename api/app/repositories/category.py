import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
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


def category_find_all_by_user_id(
    db: Session,
    user_id: uuid.UUID,
) -> list[Category]:
    return list(db.scalars(select(Category).where(Category.user_id == user_id)))


def category_find_or_create_default(
    db: Session,
    user_id: uuid.UUID,
    category_name: str,
    category_description: str | None,
) -> Category:
    statement = select(Category).where(Category.user_id == user_id, Category.category_name == category_name)
    existing = db.scalar(statement)
    if existing is not None:
        return existing

    try:
        with db.begin_nested():
            category = Category(user_id=user_id, category_name=category_name, category_description=category_description, is_default=True)
            db.add(category)
        return category
    except IntegrityError:
        return db.scalar(statement)
