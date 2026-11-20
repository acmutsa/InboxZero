class GmailServiceError(Exception):
    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code
        
class MissingScopesError(Exception):
    def __init__(self, missing: list[str]):
        super().__init__(f"Missing scopes: {', '.join(missing)}")
        self.missing = missing