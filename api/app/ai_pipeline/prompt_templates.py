

import json
import re

from langchain.agents.middleware import AgentMiddleware
from langchain.agents.middleware import ModelRequest
from langchain.agents.middleware import dynamic_prompt

from app.models.user_context import FALLBACK_NAME
from app.models.user_context import CategoryOption
from app.models.user_context import UserContext

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
        "sign_off": json.dumps(sign_off)[1:-1],
        "sign_off_placeholder": sign_off_placeholder,
        "categories": format_categories(user.categories),
    }


def format_categories(categories: tuple[CategoryOption, ...] | list[CategoryOption]) -> str:
    """Bullet list of each category's name and description."""
    if not categories:
        return "- (no categories: use null for category)"
    return "\n".join(
        f"- {category.name}: {category.description}" if category.description else f"- {category.name}"
        for category in categories
    )


def render_prompt(template: str, user: UserContext) -> str:
    values = prompt_values(user)

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        if name not in values:
            raise KeyError(f"Unknown prompt placeholder {{{{{name}}}}}")
        return values[name]

    return _PLACEHOLDER.sub(replace, template)


def user_prompt_middleware(template: str) -> AgentMiddleware:

    @dynamic_prompt
    def render_for_user(request: ModelRequest) -> str:
        return render_prompt(template, request.runtime.context)

    return render_for_user
