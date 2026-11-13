from datetime import datetime
from datetime import timezone
from typing import Literal
from typing import Optional

from pydantic import BaseModel


class WatchRequest(BaseModel):
    topicName: str
    labelIds: list[str] = ["INBOX"]
    labelFilterBehavior: Literal["INCLUDE", "EXCLUDE"] = "INCLUDE"


class WatchResponse(BaseModel):
    historyId: str
    expiration: Optional[str] = None

    @property
    def expires_at(self) -> Optional[datetime]:
        if self.expiration is None: return None
        return datetime.fromtimestamp(int(self.expiration) / 1000, tz=timezone.utc)
