"""InboxZero SQLAlchemy mappings for the PostgreSQL schema."""

from __future__ import annotations

import enum
import uuid

from datetime import date
from datetime import datetime

from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import Enum
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Text
from sqlalchemy import UniqueConstraint
from sqlalchemy import text

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

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
    __table_args__ = (Index("uq_users_clerk_id_active", "clerk_id", unique=True, postgresql_where=text("deleted_at IS NULL")),)

    clerk_id: Mapped[str] = mapped_column(Text, nullable=False)
    first_name: Mapped[str | None] = mapped_column(Text)
    last_name: Mapped[str | None] = mapped_column(Text)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    email_accounts: Mapped[list[EmailAccount]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    settings: Mapped[Settings | None] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    important_email_addresses: Mapped[list[ImportantEmailAddress]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    subscription: Mapped[Subscription | None] = relationship(back_populates="user", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    categories: Mapped[list[Category]] = relationship(back_populates="user", cascade="all, delete-orphan", passive_deletes=True)


class EmailAccount(Base):
    __tablename__ = "email_accounts"
    __table_args__ = (Index("uq_email_accounts_email_account_active", "email_account", unique=True, postgresql_where=text("deleted_at IS NULL")),)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"), nullable=False)
    email_account: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[EmailServiceProvider] = mapped_column(email_service_provider, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    gmail_history_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    gmail_watch_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[User] = relationship(back_populates="email_accounts")
    token: Mapped[EmailAccountToken | None] = relationship(back_populates="email_account", uselist=False, cascade="all, delete-orphan", passive_deletes=True)
    emails: Mapped[list[Email]] = relationship(back_populates="email_account", cascade="all, delete-orphan", passive_deletes=True)
    drafts: Mapped[list[Draft]] = relationship(back_populates="email_account", cascade="all, delete-orphan", passive_deletes=True)


class EmailAccountToken(Base):
    __tablename__ = "email_account_tokens"
    __table_args__ = (UniqueConstraint("email_account_id", name="uq_email_account_tokens_email_account_id"),)

    email_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_accounts.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"), nullable=False)
    authentication_token: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    email_account: Mapped[EmailAccount] = relationship(back_populates="token")


class Email(Base):
    __tablename__ = "emails"

    email_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_accounts.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", deferrable=True, initially="DEFERRED"), nullable=False)
    from_address: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)

    email_account: Mapped[EmailAccount] = relationship(back_populates="emails")
    category: Mapped[Category] = relationship(back_populates="emails")
    drafts: Mapped[list[Draft]] = relationship(back_populates="email", cascade="all", passive_deletes=True)


class Draft(Base):
    __tablename__ = "drafts"

    email_account_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("email_accounts.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("categories.id", deferrable=True, initially="DEFERRED"), nullable=False)
    reply_to_email: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("emails.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"))
    to_address: Mapped[str] = mapped_column(Text, nullable=False)
    subject: Mapped[str | None] = mapped_column(Text)
    body: Mapped[str | None] = mapped_column(Text)
    status: Mapped[DraftStatus | None] = mapped_column(draft_status, server_default=text("'in_review'"))

    email_account: Mapped[EmailAccount] = relationship(back_populates="drafts")
    email: Mapped[Email | None] = relationship(back_populates="drafts")
    category: Mapped[Category] = relationship(back_populates="drafts")
    check_point: Mapped[CheckPoint | None] = relationship(back_populates="draft", uselist=False, cascade="all, delete-orphan", passive_deletes=True)


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (UniqueConstraint("user_id", "category_name", name="uq_categories_user_id_category_name"),)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"), nullable=False)
    category_name: Mapped[str] = mapped_column(Text, nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    category_description: Mapped[str | None] = mapped_column(Text)

    user: Mapped[User] = relationship(back_populates="categories")
    emails: Mapped[list[Email]] = relationship(back_populates="category", passive_deletes="all")
    drafts: Mapped[list[Draft]] = relationship(back_populates="category", passive_deletes="all")


class CheckPoint(Base):
    __tablename__ = "check_points"

    draft_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("drafts.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"), unique=True, nullable=False)
    langgraph_thread_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), unique=True)
    ai_model: Mapped[str | None] = mapped_column(Text)

    draft: Mapped[Draft] = relationship(back_populates="check_point", uselist=False)


class Settings(Base):
    __tablename__ = "settings"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"), unique=True, nullable=False)
    auto_reply: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    calendar_scheduling: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    draft_with_own_voice: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    user: Mapped[User] = relationship(back_populates="settings")


class ImportantEmailAddress(Base):
    __tablename__ = "important_email_addresses"
    __table_args__ = (UniqueConstraint("user_id", "email_address", name="uq_important_email_addresses_user_id_email_address"),)

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"), nullable=False)
    email_address: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped[User] = relationship(back_populates="important_email_addresses")


class Subscription(Base):
    __tablename__ = "subscriptions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE", deferrable=True, initially="IMMEDIATE"), unique=True, nullable=False)
    tier: Mapped[SubscriptionTier] = mapped_column(subscription_tier, nullable=False, server_default=text("'free'"))
    expiration: Mapped[date | None] = mapped_column(Date)

    user: Mapped[User] = relationship(back_populates="subscription")
