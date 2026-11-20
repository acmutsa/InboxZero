from pydantic import ValidationError

from app.ai_pipeline.settings import pipeline_settings
from app.ai_pipeline.states import BinValidate,EmailState,DraftValidate


def extract_json(raw_output: str | None) -> str:
    """Pull the JSON object out of an LLM reply.

    Models often wrap JSON in a ```json fence or add a sentence around it even
    when told to respond with JSON only. Validation still decides whether the
    result is acceptable; this only removes the wrapping.
    """
    text = (raw_output or "").strip()

    # A fenced reply: drop the opening ``` line (with or without "json") and the closing ```.
    # Only when the whole reply starts with a fence, so ``` inside a draft body is left alone.
    if text.startswith("```"):
        first_newline = text.find("\n")
        text = text[first_newline + 1:] if first_newline != -1 else text[3:]
        text = text.rstrip()
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    # Prose around the object: keep from the first "{" to the last "}".
    if not text.startswith("{"):
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            text = text[start:end + 1]

    return text


def email_binning_gate(state: EmailState) -> dict:
    # Gate 2: check that the LLM's JSON matches the BinValidate model
    try:
        result = BinValidate.model_validate_json(extract_json(state["raw_output"]))
    except ValidationError as e:
        return {
            "error": f"invalid bin output: {e}",
            "attempts": state["attempts"] + 1,
        }

    # Only go on to drafting when a reply is needed and the classifier is sure enough.
    skip_reason = None
    threshold = pipeline_settings.bin_confidence_threshold
    if not result.needs_reply:
        skip_reason = f"no reply needed: {result.reason}"
    elif result.confidence < threshold:
        skip_reason = f"low confidence ({result.confidence:.2f} < {threshold:.2f}): {result.reason}"

    # Reset the counter so the drafting step gets its own retries.
    return {"bin_result": result, "skip_reason": skip_reason, "error": None, "attempts": 0}



def email_drafting_gate(state: EmailState)-> dict:
    # Gate 3: check the draft's JSON and content rules (see DraftValidate)
    try:
        result = DraftValidate.model_validate_json(extract_json(state["raw_output"]))
    except ValidationError as e:
        return {
            "error": f"invalid draft output: {e}",
            "attempts": state["attempts"] + 1,
            }

    return {"draft_result": result, "error": None, "attempts": 0}


def route_after_gate(state: EmailState) -> str:
    """Shared router for all three gates."""
    if state.get("skip_reason"):
        return "Skip"
    if state.get("error") is None:
        return "Success"
    if state.get("attempts", 0) > pipeline_settings.max_retries:
        return "GiveUp"
    return "Error"
