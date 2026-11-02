async def process_email(account_id: str, message_id: str):
    """
    Temporary mock workflow for testing ARQ integration.
    """

    print(f"Processing email {message_id} for account {account_id}")

    return {
        "status": "completed",
        "account_id": account_id,
        "message_id": message_id,
        "classification": "mock",
        "draft": None
    }