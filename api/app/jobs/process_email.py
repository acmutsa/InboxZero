import logging
import uuid

from app.ai_pipeline.settings import pipeline_settings
from app.ai_pipeline.states import DraftValidate
from app.ai_pipeline.states import EmailState
from app.ai_pipeline.thread_context import build_previous_message
from app.ai_pipeline.thread_context import build_thread_context
from app.ai_pipeline.thread_context import find_previous_message_id
from app.ai_pipeline.thread_context import strip_quoted_reply
from app.ai_pipeline.thread_context import truncate
from app.ai_pipeline.categorize import load_category_options
from app.ai_pipeline.user_context import UserContext
from app.db.session import SessionLocal
from app.email_service.provider import EmailProvider
from app.email_service.registry import get_email_provider
from app.email_service.types.draft import ReplyDraft
from app.email_service.types.error import EmailServiceError
from app.email_service.types.error import UnsupportedProviderError
from app.email_service.types.message import EmailMessage
from app.email_service.types.message import EmailThread
from app.repositories.draft import draft_create_for_email
from app.repositories.draft import draft_find_one_by_email_id
from app.repositories.email import email_find_one_by_email_id

logger = logging.getLogger(__name__)


def process_email(email_id: str) -> None:
    email_uuid = uuid.UUID(email_id)
    loaded = _load_email(email_uuid)
    if loaded is None:
        return

    provider, user, message, thread, previous = loaded
    state = build_initial_state(message, thread, user, previous, provider=provider, email_id=email_uuid)

    from app.ai_pipeline.pipeline import email_graph

    result = email_graph.invoke(state)
    draft = result.get("draft_result")
    logger.info(
        "Email processed",
        extra={
            "email_id": email_id,
            "thread_id": state["thread"].thread_id,
            "skip_reason": result.get("skip_reason"),
            "category": result["category"].name if result.get("category") else None,
            "categorize_skip_reason": result.get("categorize_skip_reason"),
            "error": result.get("error"),
            "drafted": draft is not None,
        },
    )

    if draft is not None:
        _save_draft(provider, email_uuid, message, reply_to_address(state["headers"]), draft)


def reply_to_address(headers: dict) -> str:
    return headers.get("reply-to") or headers.get("from") or ""


def _save_draft(
    provider: EmailProvider,
    email_id: uuid.UUID,
    original: EmailMessage,
    to_address: str,
    draft: DraftValidate,
) -> None:
    if not to_address:
        logger.warning("Not saving draft: the email has no address to reply to", extra={"email_id": str(email_id)})
        return

    with SessionLocal() as db:
        email = email_find_one_by_email_id(db, email_id)
        if email is None:
            logger.info("Not saving draft: the email was deleted while it was drafted", extra={"email_id": str(email_id)})
            return

        saved = draft_create_for_email(db, email, to_address=to_address, subject=draft.subject, body=draft.body)
        draft_row_id = saved.id
        provider_draft_id = provider.create_reply_draft(
            original,
            ReplyDraft(to_address=to_address, subject=draft.subject, body=draft.body),
        )
        saved.provider_draft_id = provider_draft_id
        db.commit()

    logger.info(
        "Draft saved",
        extra={"email_id": str(email_id), "draft_id": str(draft_row_id), "provider_draft_id": provider_draft_id},
    )


def build_initial_state(
    message: EmailMessage,
    thread: EmailThread,
    user: UserContext,
    previous: EmailMessage | None = None,
    provider: EmailProvider | None = None,
    email_id: uuid.UUID | None = None,
) -> EmailState:
    body = truncate(strip_quoted_reply(message.text or ""), pipeline_settings.body_max_chars)
    return {
        "user": user,
        "provider": provider,
        "email_id": email_id,
        "message_id": message.id,
        "label_ids": sorted(message.labels),
        "headers": dict(message.headers),
        "body": body,
        "thread": build_thread_context(message, thread),
        "previous_message": (
            build_previous_message(previous, pipeline_settings.previous_message_max_chars)
            if previous is not None
            else None
        ),
        "raw_output": None,
        "parsed": None,
        "bin_result": None,
        "draft_result": None,
        "skip_reason": None,
        "categorize_skip_reason": None,
        "category": None,
        "error": None,
        "attempts": 0,
    }


def _load_email(
    email_id: uuid.UUID,
) -> tuple[EmailProvider, UserContext, EmailMessage, EmailThread, EmailMessage | None] | None:
    with SessionLocal() as db:
        email = email_find_one_by_email_id(db, email_id)

        if email is None:
            logger.warning("Skipping processing for an email that no longer exists", extra={"email_id": str(email_id)})
            return None

        if draft_find_one_by_email_id(db, email_id) is not None:
            logger.info("Skipping processing for an email that already has a draft", extra={"email_id": str(email_id)})
            return None

        if email.provider_message_id is None:
            logger.warning("Skipping processing for an email without a provider message id", extra={"email_id": str(email_id)})
            return None

        account = email.email_account

        if account.deleted_at is not None:
            logger.info("Skipping processing for a disconnected account", extra={"email_id": str(email_id)})
            return None

        try:
            provider = get_email_provider(account)
        except UnsupportedProviderError:
            logger.warning("Skipping processing for an unsupported provider", extra={"email_id": str(email_id), "provider": str(account.provider)})
            return None

        provider_message_id = email.provider_message_id
        user = UserContext(
            user_id=account.user_id,
            email=account.email_account,
            first_name=account.user.first_name,
            last_name=account.user.last_name,
            categories=tuple(load_category_options(db, account.user_id)),
        )

    try:
        message = provider.get_message(provider_message_id)
        thread = provider.get_thread(message.thread_id)
    except EmailServiceError as error:
        if error.status_code == 404:
            logger.info("Message was deleted before it could be processed", extra={"email_id": str(email_id)})
            return None
        raise

    previous = None
    previous_id = find_previous_message_id(message, thread)
    if previous_id is not None:
        try:
            previous = provider.get_message(previous_id)
        except EmailServiceError as error:
            if error.status_code != 404:
                raise
            logger.info("Previous message in thread was deleted", extra={"email_id": str(email_id)})

    return provider, user, message, thread, previous
