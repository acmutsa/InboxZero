from pydantic import ValidationError

from app.ai_pipeline.settings import pipeline_settings
from app.ai_pipeline.states import BinValidate,EmailState,DraftValidate


def extract_json(raw_output: str | None) -> str:
    text = (raw_output or "").strip()

    if text.startswith("```"):
        first_newline = text.find("\n")
        text = text[first_newline + 1:] if first_newline != -1 else text[3:]
        text = text.rstrip()
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            text = text[start:end + 1]

    return text


def email_binning_gate(state: EmailState) -> dict:
    try:
        result = BinValidate.model_validate_json(extract_json(state["raw_output"]))
    except ValidationError as e:
        return {
            "error": f"invalid bin output: {e}",
            "attempts": state["attempts"] + 1,
        }

    category = None
    user = state.get("user")
    if state.get("categorize_skip_reason") is None and user is not None and user.categories:
        category = user.find_category(result.category)
        if category is None:
            allowed = ", ".join(c.name for c in user.categories)
            return {
                "error": f"invalid bin output: unknown category {result.category!r}; expected one of: {allowed}",
                "attempts": state["attempts"] + 1,
            }

    skip_reason = None
    threshold = pipeline_settings.bin_confidence_threshold
    if not result.needs_reply:
        skip_reason = f"no reply needed: {result.reason}"
    elif result.confidence < threshold:
        skip_reason = f"low confidence ({result.confidence:.2f} < {threshold:.2f}): {result.reason}"

    return {"bin_result": result, "category": category, "skip_reason": skip_reason, "error": None, "attempts": 0}



def email_drafting_gate(state: EmailState)-> dict:
    try:
        result = DraftValidate.model_validate_json(extract_json(state["raw_output"]))
    except ValidationError as e:
        return {
            "error": f"invalid draft output: {e}",
            "attempts": state["attempts"] + 1,
            }

    return {"draft_result": result, "error": None, "attempts": 0}


def route_after_bin_gate(state: EmailState) -> str:
    if state.get("error") is not None:
        return _retry_or_give_up(state)
    return "Categorize"


def route_after_categorize(state: EmailState) -> str:
    if state.get("skip_reason"):
        return "Skip"
    return "Draft"


def route_after_gate(state: EmailState) -> str:
    if state.get("skip_reason"):
        return "Skip"
    if state.get("error") is None:
        return "Success"
    return _retry_or_give_up(state)


def _retry_or_give_up(state: EmailState) -> str:
    if state.get("attempts", 0) > pipeline_settings.max_retries:
        return "GiveUp"
    return "Error"
