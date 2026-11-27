from app.email_service.types.error import EmailServiceError

class GmailServiceError(EmailServiceError):
    pass

class MissingScopesError(Exception):
    def __init__(self, missing: list[str]):
        super().__init__(f"Missing scopes: {', '.join(missing)}")
        self.missing = missing
