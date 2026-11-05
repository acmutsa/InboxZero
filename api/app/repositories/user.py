from datetime import datetime
from datetime import timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.schema import Settings
from app.db.schema import Subscription
from app.db.schema import User


def get_user_by_clerk_id(
    db: Session, 
    clerk_id: str
) -> User | None:
    return db.scalar(select(User).where(User.clerk_id == clerk_id, User.deleted_at.is_(None)))


def create_user(
    db: Session, 
    clerk_id: str, 
    first_name: str | None = None, 
    last_name: str | None = None
) -> User:
    user = User(
        clerk_id=clerk_id,
        first_name=first_name,
        last_name=last_name,
        settings=Settings(),
        subscription=Subscription(),
    )
    db.add(user)
    db.flush()
    return user


def update_user(
    db: Session, 
    user: User, 
    first_name: str | None, 
    last_name: str | None
) -> User:
    user.first_name = first_name
    user.last_name = last_name
    db.flush()
    return user


def delete_user(
    db: Session, 
    user: User
) -> None:
    """Soft delete the user"""
    deleted_at = datetime.now(timezone.utc)
    user.deleted_at = deleted_at

    for account in user.email_accounts:
        if account.deleted_at is None:
            account.deleted_at = deleted_at
            account.token = None

    db.flush()
