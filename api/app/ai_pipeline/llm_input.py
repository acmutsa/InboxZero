from app.ai_pipeline.settings import pipeline_settings
from  app.ai_pipeline.types.email_state import EmailState
import re 

def format_email_for_llm(state: EmailState) -> str:
    headers = state.get("headers") or {}
    lines = [
        f"Sender: {headers.get('from', '(unknown sender)')}",
        f"Subject: {headers.get('subject', '(no subject)')}",
        "Body:",
        state.get("body") or "(empty)",
    ]

    previous = state.get("previous_message")
    if previous is not None:
        # Same wording as the prompt examples: "(sent by <name or user>)".
        who = f"sent by {state['user'].display_name}" if previous.is_sent else f"from {previous.sender or '(unknown sender)'}"
        text = truncate(strip_quoted_reply(previous.text or ""), pipeline_settings.previous_message_max_chars)
        lines += [
            "",
            f"Previous message ({who}):",
            text or "(empty)",
        ]

    return "\n".join(lines) + "\n"

# Lines that mark where a reply's quoted history begins. strip_quoted_reply cuts
# the text at the earliest match, so only what the sender wrote reaches the LLM.
# English only: other languages' quote lines (e.g. "Le ... a écrit :") are not caught.
_QUOTE_STARTS = (
    # Gmail / Apple Mail: "On Tue, Nov 3, 2026 at 2:00 PM Sam <sam@x.com> wrote:".
    # Allows up to 2 extra lines because clients wrap long names and addresses.
    re.compile(r"^On (?:[^\n]*\n){0,2}?[^\n]*wrote:[ \t]*$", re.MULTILINE),
    # Outlook desktop: "-----Original Message-----".
    re.compile(r"^-{2,}\s*Original Message\s*-{2,}", re.MULTILINE | re.IGNORECASE),
    # Newer Outlook: a line of underscores followed by "From: ...". Requiring the
    # "From:" line keeps an ordinary underscore divider from cutting the text.
    re.compile(r"^_{10,}[ \t]*\nFrom: ", re.MULTILINE),
)

def strip_quoted_reply(text: str) -> str:
    text = text.replace("\r\n", "\n")
    cut = min((m.start() for pattern in _QUOTE_STARTS if (m := pattern.search(text))), default=len(text))
    own_text = text[:cut]
    lines = [line for line in own_text.splitlines() if not line.lstrip().startswith(">")]
    return "\n".join(lines).strip()


def truncate(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rstrip() + "\n[... truncated]"