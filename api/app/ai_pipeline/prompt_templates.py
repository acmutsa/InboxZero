"""Fill the {{...}} placeholders in the prompt files for one user.

When the user has a name stored it is used; otherwise every placeholder falls
back to the generic wording ("user", and a [your name] sign-off placeholder).
"""

import json
import re

from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware import ModelRequest
from langchain.agents.middleware import dynamic_prompt

from app.ai_pipeline.user_context import FALLBACK_NAME
from app.ai_pipeline.user_context import UserContext

SIGN_OFF_PLACEHOLDER = "[your name]"

_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def prompt_values(user: UserContext) -> dict[str, str]:
    first_name = user.first_name

    if first_name:
        sign_off_rule = f"- Sign off with {first_name} on its own line"
        sign_off = first_name
        sign_off_placeholder = ""
    else:
        sign_off_rule = (
            f"- Sign off with the placeholder {SIGN_OFF_PLACEHOLDER} on its own line. "
            'Never write an actual name there, and list it in "placeholders"'
        )
        sign_off = SIGN_OFF_PLACEHOLDER
        sign_off_placeholder = f", {json.dumps(SIGN_OFF_PLACEHOLDER)}"

    return {
        "user": user.display_name,
        "user_first_name": first_name or FALLBACK_NAME,
        "sign_off_rule": sign_off_rule,
        # Used inside the JSON examples, so escape it as a JSON string body.
        "sign_off": json.dumps(sign_off)[1:-1],
        # Appended to an example's "placeholders" list: nothing when the name is known.
        "sign_off_placeholder": sign_off_placeholder,
    }


def render_prompt(template: str, user: UserContext) -> str:
    values = prompt_values(user)

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in values:
            # A typo in a prompt file would otherwise reach the model as literal text.
            raise KeyError(f"Unknown prompt placeholder {{{{{name}}}}}")
        return values[name]

    return _PLACEHOLDER.sub(replace, template)


def user_prompt_middleware(template: str) -> AgentMiddleware:
    """Agent middleware that renders `template` for the user passed as the run's context."""

    @dynamic_prompt
    def render_for_user(request: ModelRequest) -> str:
        return render_prompt(template, request.runtime.context)

    return render_for_user
