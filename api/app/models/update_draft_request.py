from typing import Annotated

from pydantic import BaseModel
from pydantic import StringConstraints

from app.db.schema import DraftStatus


class UpdateDraftRequest(BaseModel):
    body: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)] | None = None
    status: DraftStatus | None = None
