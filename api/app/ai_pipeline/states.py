from typing_extensions import TypedDict

class EmailState(TypedDict):
    label_ids: list[str]        # was str
    header: dict
    body: str
    raw_output: str | None      # was str
    parsed: dict | None
    error: str | None
    attempts: int
