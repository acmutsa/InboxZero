
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


def utc_now():
    return datetime.now(timezone.utc)


class OutlookAccount(Base):
    __tablename__ = "outlook_accounts"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "microsoft_account_id",
            name="uq_outlook_user_microsoft_account",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    user_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )

    microsoft_account_id: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(320), nullable=False
    )

    access_token_encrypted: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    refresh_token_encrypted: Mapped[str] = mapped_column(
        Text, nullable=False
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
