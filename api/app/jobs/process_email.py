
import logging
import uuid

from app.ai_pipeline.reply_draft import build_reply_draft_request
from app.ai_pipeline.settings import pipeline_settings
from app.ai_pipeline.states import DraftValidate
from app.ai_pipeline.states import EmailState
from app.ai_pipeline.thread_context import ThreadContext
from app.ai_pipeline.thread_context import build_previous_message
from app.ai_pipeline.thread_context import build_thread_context
from app.ai_pipeline.thread_context import find_previous_message_id
from app.ai_pipeline.thread_context import strip_quoted_reply
from app.ai_pipeline.thread_context import truncate
from app.ai_pipeline.user_context import UserContext
from app.db.schema import EmailServiceProvider
from app.db.session import SessionLocal
from app.email_service.gmail.gmail import GmailService
from app.email_service.gmail.token_manager import GmailTokenManager
from app.email_service.gmail.types.error import GmailServiceError
from app.email_service.gmail.types.message import Message
from app.email_service.gmail.types.message_request import MessageRequest
from app.email_service.gmail.types.thread import Thread
from app.email_service.gmail.types.thread import ThreadRequest
from app.repositories.draft import draft_create_for_email
from app.repositories.draft import draft_find_one_by_email_id
from app.repositories.email import email_find_one_by_email_id

logger = logging.getLogger(__name__)


def process_email(email_id: str) -> None:
    email_uuid = uuid.UUID(email_id)
    loaded = _load_from_gmail(email_uuid)
    if loaded is None:
        return

    gmail, user, message, thread, previous = loaded
    state = build_initial_state(message, thread, user, previous)

    from app.ai_pipeline.pipeline import email_graph

    result = email_graph.invoke(state)
    draft = result.get("draft_result")
    logger.info(
        "Email processed",
        extra={
            "email_id": email_id,
            "thread_id": state["thread"].thread_id,
            "skip_reason": result.get("skip_reason"),
            "error": result.get("error"),
            "drafted": draft is not None,
        },
    )

    if draft is not None:
        _save_draft(gmail, email_uuid, reply_to_address(state["headers"]), state["thread"], draft)


def reply_to_address(headers: dict) -> str:
    """Where a reply goes: Reply-To if the sender set one, otherwise From. Headers are lowercased."""
    return headers.get("reply-to") or headers.get("from") or ""


def _save_draft(
    gmail: GmailService,
    email_id: uuid.UUID,
    to_address: str,
    thread: ThreadContext,
    draft: DraftValidate,
) -> None:
    """Save the reply to the drafts table and to the user's Gmail drafts."""
    if not to_address:
        logger.warning("Not saving draft: the email has no address to reply to", extra={"email_id": str(email_id)})
        return

    with SessionLocal() as db:
        email = email_find_one_by_email_id(db, email_id)
        if email is None:
            logger.info("Not saving draft: the email was deleted while it was drafted", extra={"email_id": str(email_id)})
            return

        # Add the row first and commit only once Gmail has accepted the draft.
        # If Gmail fails, the row is rolled back and a retry starts clean.
        saved = draft_create_for_email(db, email, to_address=to_address, subject=draft.subject, body=draft.body)
        draft_row_id = saved.id
        gmail_draft = gmail.post_draft(
            build_reply_draft_request(
                to_address=to_address,
                subject=draft.subject,
                body=draft.body,
                thread_id=thread.thread_id,
                in_reply_to=thread.message_id_header,
                references=thread.reply_references,
            )
        )
        saved.gmail_draft_id = gmail_draft.id
        db.commit()

    logger.info(
        "Draft saved",
        extra={"email_id": str(email_id), "draft_id": str(draft_row_id), "gmail_draft_id": gmail_draft.id},
    )



def build_initial_state(
    message: Message,
    thread: Thread,
    user: UserContext,
    previous: Message | None = None,
) -> EmailState:
    headers = {h.name.lower(): h.value for h in message.payload.headers} if message.payload else {}

    body = truncate(strip_quoted_reply(message.text or ""), pipeline_settings.body_max_chars)
    return {
        "user": user,
        "label_ids": message.labelIds,
        "headers": headers,
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
        "error": None,
        "attempts": 0,
    }


def _load_from_gmail(
    email_id: uuid.UUID,
) -> tuple[GmailService, UserContext, Message, Thread, Message | None] | None:

    with SessionLocal() as db:
        email = email_find_one_by_email_id(db, email_id)

        if email is None:
            logger.warning("Skipping processing for an email that no longer exists", extra={"email_id": str(email_id)})
            return None

        # A retried job must not draft (and post to Gmail) a second time.
        if draft_find_one_by_email_id(db, email_id) is not None:
            logger.info("Skipping processing for an email that already has a draft", extra={"email_id": str(email_id)})
            return None

        if email.gmail_message_id is None:
            logger.warning("Skipping processing for an email without a Gmail message id", extra={"email_id": str(email_id)})
            return None

        account = email.email_account

        if account.deleted_at is not None or account.provider != EmailServiceProvider.gmail:
            logger.info("Skipping processing for a disconnected or non-Gmail account", extra={"email_id": str(email_id)})
            return None

        gmail = GmailService(GmailTokenManager(account))
        gmail_message_id = email.gmail_message_id
        user = UserContext(
            email=account.email_account,
            first_name=account.user.first_name,
            last_name=account.user.last_name,
        )

    try:
        message = gmail.get_message(MessageRequest(id=gmail_message_id))
        # Metadata is enough for the thread: labels, dates and headers, no bodies.
        thread = gmail.get_thread(ThreadRequest(id=message.threadId or message.id, format="metadata"))
    except GmailServiceError as error:
        if error.status_code == 404:
            logger.info("Gmail message was deleted before it could be processed", extra={"email_id": str(email_id)})
            return None
        raise

    previous = None
    previous_id = find_previous_message_id(message, thread)
    if previous_id is not None:
        try:
            previous = gmail.get_message(MessageRequest(id=previous_id))
        except GmailServiceError as error:
            if error.status_code != 404:
                raise
            # Deleted since the thread was read; carry on without the context.
            logger.info("Previous message in thread was deleted", extra={"email_id": str(email_id)})

    return gmail, user, message, thread, previous
