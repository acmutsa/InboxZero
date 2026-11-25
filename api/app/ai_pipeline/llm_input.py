from app.ai_pipeline.states import EmailState


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
        who = f"sent by {state['user'].display_name}" if previous.sent_by_user else f"from {previous.from_address}"
        lines += [
            "",
            f"Previous message ({who}):",
            previous.text or "(empty)",
        ]

    return "\n".join(lines) + "\n"
