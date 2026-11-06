from states import EmailState
from agents import agent_bin,agent_draft
import re
from email.utils import parseaddr

def ai_bin_node(state: EmailState):
    out = agent_bin.invoke({"messages": [("user", state["request"])]})
    #print(out)
    return {"result": out["messages"][-1].text}

def ai_draft_node(state: EmailState):
    out = agent_draft.invoke(
        {"messages": [("user",
            f"Multiply {state['result']} by {state['mul_context']}.")]}
    )
    #print(out)
    return {"result": out["messages"][-1].text}


def code_check_node(state:EmailState):
   
    reason = skip_reason(state["label_ids"], state["headers"])
    if reason:
        return {"error": f"skipped: {reason}"}
    return {}


def route_after_code_node(state:EmailState):

    if state["error"]:
        return "Error"
    return "Success"


def handle_failure(state: EmailState):
    print(f"Failed at: {state['error']}")
    return {}

# Helper functions


NO_REPLY_KEYWORDS = [
    "noreply", "donotreply", "dontreply",
    "notmonitored", "unmonitored", "unattended",
    "mailerdaemon", "postmaster", "bounce", "autoreply", "autoconfirm",
    ]

def is_no_reply(header_from: str) -> bool:
    #True if the sender looks like a no-reply 
    _, email = parseaddr(header_from)         
    local_part = email.split("@")[0].lower()   
    normalized = re.sub(r"[^a-z0-9]", "", local_part)   # drop - _ . +
    return any(word in normalized for word in NO_REPLY_KEYWORDS)
    pass

SKIP_LABELS = {"SPAM", "TRASH", "SENT", "CATEGORY_PROMOTIONS", "CATEGORY_SOCIAL", "CATEGORY_FORUMS"}
AUTO_SUBJECTS = ("automatic reply", "out of office", "undeliverable",
                 "delivery status notification", "mail delivery failed", "auto:")
MY_EMAIL = "you@example.com"


def skip_reason(labels, headers: dict) -> str | None:
    """Return why an email should be skipped, or None if it looks fine to process."""
    labels = set(labels)
    h = {k.lower(): v for k, v in headers.items()}   # case-insensitive headers
    sender = parseaddr(h.get("from", ""))[1].lower()
    subject = h.get("subject", "").lower()

    if labels & SKIP_LABELS:
        return f"label: {', '.join(labels & SKIP_LABELS)}"
    if sender == MY_EMAIL:
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
