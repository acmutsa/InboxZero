"""InboxZero SQLAlchemy mappings for the PostgreSQL schema."""

from __future__ import annotations

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class EmailServiceProvider(enum.Enum):
    gmail = "gmail"
    outlook = "outlook"


class DraftStatus(enum.Enum):
    in_review = "in_review"
    sent = "sent"


class SubscriptionTier(enum.Enum):
    free = "free"
    premium = "premium"


email_service_provider = Enum(EmailServiceProvider, name="email_service_provider", native_enum=True)
draft_status = Enum(DraftStatus, name="draft_status", native_enum=True)
subscription_tier = Enum(SubscriptionTier, name="subscription_tier", native_enum=True)


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)
    clerk_id: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))

    email_accounts: Mapped[list[EmailAccount]] = relationship(back_populates="user")
    settings: Mapped[Settings | None] = relationship(back_populates="user", uselist=False)


class EmailAccount(Base):
    __tablename__ = "email_accounts"

    email_account: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    provider: Mapped[EmailServiceProvider] = mapped_column(email_service_provider, nullable=False)
    cursor: Mapped[str | None] = mapped_column(Text)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", deferrable=True, initially="IMMEDIATE"), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))

    user: Mapped[User] = relationship(back_populates="email_accounts")
    tokens: Mapped[list[EmailAccountToken]] = relationship(back_populates="email_account")
    emails: Mapped[list[Email]] = relationship(back_populates="email_account")


class EmailAccountToken(Base):
    __tablename__ = "email_account_tokens"

    authentication_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    email_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_accounts.id", deferrable=True, initially="IMMEDIATE"), nullable=False)

    email_account: Mapped[EmailAccount] = relationship(back_populates="tokens")


class Email(Base):
    __tablename__ = "emails"

    from_address: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str | None] = mapped_column(Text)
    draft_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("drafts.id", deferrable=True, initially="IMMEDIATE"), unique=True)
    email_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_accounts.id", deferrable=True, initially="IMMEDIATE"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", deferrable=True, initially="IMMEDIATE"), nullable=False)

    draft: Mapped[Draft | None] = relationship(back_populates="email", uselist=False)
    email_account: Mapped[EmailAccount] = relationship(back_populates="emails")
    category: Mapped[Category] = relationship(back_populates="emails")


class Draft(Base):
    __tablename__ = "drafts"

    status: Mapped[DraftStatus | None] = mapped_column(draft_status, server_default=text("'in_review'"))

    email: Mapped[Email | None] = relationship(back_populates="draft", uselist=False)
    check_point: Mapped[CheckPoint | None] = relationship(back_populates="draft", uselist=False)


class Category(Base):
    __tablename__ = "categories"

    category_name: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    category_description: Mapped[str | None] = mapped_column(Text)

    emails: Mapped[list[Email]] = relationship(back_populates="category")


class CheckPoint(Base):
    __tablename__ = "check_points"

    langgraph_thread_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), unique=True)
    ai_model: Mapped[str | None] = mapped_column(Text)
    draft_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("drafts.id", deferrable=True, initially="IMMEDIATE"), unique=True, nullable=False)

    draft: Mapped[Draft] = relationship(back_populates="check_point", uselist=False)


class Settings(Base):
    __tablename__ = "settings"

    auto_reply: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    calendar_scheduling: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    draft_with_own_voice: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", deferrable=True, initially="IMMEDIATE"), unique=True, nullable=False)

    user: Mapped[User] = relationship(back_populates="settings")
    important_email_addresses: Mapped[list[ImportantEmailAddress]] = relationship(back_populates="setting")
    subscription: Mapped[Subscription | None] = relationship(back_populates="setting", uselist=False)


class ImportantEmailAddress(Base):
    __tablename__ = "important_email_addresses"

    email_address: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    setting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("settings.id", deferrable=True, initially="IMMEDIATE"), nullable=False)

    setting: Mapped[Settings] = relationship(back_populates="important_email_addresses")


class Subscription(Base):
    __tablename__ = "subscriptions"

    tier: Mapped[SubscriptionTier] = mapped_column(subscription_tier, nullable=False, server_default=text("'free'"))
    setting_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("settings.id", deferrable=True, initially="IMMEDIATE"), unique=True, nullable=False)
    expiration: Mapped[date | None] = mapped_column(Date)
    
    setting: Mapped[Settings] = relationship(back_populates="subscription")
