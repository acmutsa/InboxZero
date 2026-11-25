from app.ai_pipeline.states import EmailState
from app.ai_pipeline.agents import agent_bin,agent_draft
from app.ai_pipeline.llm_input import format_email_for_llm
from app.ai_pipeline.categorize import categorize_skip_reason
from app.ai_pipeline.thread_context import thread_skip_reason
from app.db.session import SessionLocal
from app.email_service.types.error import EmailServiceError
from app.email_service.types.message import MessageLabel
from app.repositories.category import category_find_or_create_default
from app.repositories.email import email_set_category
import logging
import re
from email.utils import parseaddr
from app.constants import AUTO_SUBJECTS
from app.constants import NO_REPLY_KEYWORDS


logger = logging.getLogger(__name__)


def ai_bin_node(state: EmailState):
    out = agent_bin.invoke({"messages": [("user", format_email_for_llm(state))]}, context=state["user"])
    return {"raw_output": out["messages"][-1].text}

def ai_draft_node(state: EmailState):
    out = agent_draft.invoke({"messages": [("user", format_email_for_llm(state))]}, context=state["user"])
    return {"raw_output": out["messages"][-1].text}


def code_check_node(state:EmailState):
    reason = (
        skip_reason(state["label_ids"], state["headers"], my_email=state["user"].email)
        or thread_skip_reason(state["thread"])
    )
    return {
        "skip_reason": reason,
        "categorize_skip_reason": categorize_skip_reason(state["label_ids"], state["thread"], state["user"].categories),
    }


def categorize_node(state: EmailState):
    category = state.get("category")
    if state.get("categorize_skip_reason") is not None or category is None:
        return {}

    if state["email_id"] is not None:
        with SessionLocal() as db:
            category_id = category.id
            if category_id is None:
                category_id = category_find_or_create_default(
                    db, state["user"].user_id, category.name, category.description,
                ).id
            email_set_category(db, state["email_id"], category_id)
            db.commit()

    if state["provider"] is not None:
        try:
            state["provider"].apply_category(state["message_id"], category.name)
        except EmailServiceError:
            logger.exception(
                "Could not apply category in the mailbox",
                extra={"email_id": str(state["email_id"]), "category": category.name},
            )
    logger.info(f"Categorized: {category.name}")
    return {}


def record_skip(state: EmailState):
    logger.info(f"Skipped: {state['skip_reason']}")
    return {}


def handle_failure(state: EmailState):
    logger.info(f"Failed at: {state['error']}")
    return {}

def save_draft(state: EmailState):
    return {}


def is_no_reply(header_from: str) -> bool:
    _, email = parseaddr(header_from)         
    local_part = email.split("@")[0].lower()   
    normalized = re.sub(r"[^a-z0-9]", "", local_part)
    return any(word in normalized for word in list(NO_REPLY_KEYWORDS))



def skip_reason(labels, headers: dict, my_email: str) -> str | None:
    labels = set(labels)
    h = {k.lower(): v for k, v in headers.items()}
    sender = parseaddr(h.get("from", ""))[1].lower()
    subject = h.get("subject", "").lower()

    if sender == my_email.lower():
        return "sent by me"
    if is_no_reply(h.get("from", "")) or is_no_reply(h.get("reply-to", "")):
        return "no-reply sender"
    if h.get("auto-submitted", "no").lower() != "no":
        return "auto-submitted"
    if any(k in h for k in ("x-autoreply", "x-autorespond", "x-auto-response-suppress")):
        return "auto-responder"
    if h.get("return-path", "").strip() == "<>":
        return "bounce"
    if subject.startswith(AUTO_SUBJECTS):
        return "auto-reply subject"
    if h.get("precedence", "").lower() in ("bulk", "list", "junk"):
        return "bulk mail"
    if "list-unsubscribe" in h or "list-id" in h:
        return "mailing list"
    if any(f in h.get("authentication-results", "").lower()
           for f in ("spf=fail", "dkim=fail", "dmarc=fail")):
        return "failed authentication"
    return None
