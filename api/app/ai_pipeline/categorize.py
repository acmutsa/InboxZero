import uuid

from sqlalchemy.orm import Session

from app.models.user_context import CategoryOption
from app.constants import DEFAULT_CATEGORIES
from app.db.schema import Category
from app.email_service.types.message import MessageLabel
from app.repositories.category import category_find_all_by_user_id

CATEGORIZE_SKIP_LABELS = {MessageLabel.DRAFT, MessageLabel.SPAM, MessageLabel.TRASH, MessageLabel.SENT}


def categorize_skip_reason(labels, is_reply: bool, categories: tuple[CategoryOption, ...]) -> str | None:
    skipped = set(labels) & CATEGORIZE_SKIP_LABELS
    if skipped:
        return f"label: {', '.join(sorted(skipped))}"
    if is_reply:
        return "part of an existing thread"
    if not categories:
        return "no categories"
    return None


def merge_categories(saved: list[Category]) -> list[CategoryOption]:
    default_names = {default["category_name"].lower() for default in DEFAULT_CATEGORIES}
    saved_by_name = {category.category_name.lower(): category for category in saved}

    custom = sorted(
        (category for category in saved if category.category_name.lower() not in default_names),
        key=lambda category: category.category_name.lower(),
    )
    options = [_from_row(category) for category in custom]

    for default in DEFAULT_CATEGORIES:
        row = saved_by_name.get(default["category_name"].lower())
        options.append(
            _from_row(row) if row is not None
            else CategoryOption(name=default["category_name"], description=default["category_description"])
        )
    return options


def load_category_options(db: Session, user_id: uuid.UUID) -> list[CategoryOption]:
    return merge_categories(category_find_all_by_user_id(db, user_id))


def _from_row(category: Category) -> CategoryOption:
    return CategoryOption(id=category.id, name=category.category_name, description=category.category_description)
