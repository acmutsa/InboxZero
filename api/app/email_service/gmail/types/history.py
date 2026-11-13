from typing import Literal
from typing import Optional

from pydantic import BaseModel

from app.email_service.gmail.types.message import Message

HistoryType = Literal["messageAdded", "messageDeleted", "labelAdded", "labelRemoved"]

class HistoryListRequest(BaseModel):
    startHistoryId: str
    historyTypes: Optional[list[HistoryType]] = ["messageAdded", "messageDeleted", "labelAdded", "labelRemoved"]
    labelId: Optional[str] = None
    pageToken: Optional[str] = None
    maxResults: int = 100

class HistoryLabelChange(BaseModel):
    message: Message
    labelIds: list[str] = []

class History(BaseModel):
    id: str
    messages: list[Message] = []
    messagesAdded: list[Message] = []
    messagesDeleted: list[Message] = []
    labelsAdded: list[HistoryLabelChange] = []
    labelsRemoved: list[HistoryLabelChange] = []

class HistoryList(BaseModel):
    history: list[History] = []
    nextPageToken: Optional[str] = None
    historyId: Optional[str] = None

    @property
    def added_message_ids(self) -> list[str]:
        ids: dict[str, None] = {}
        for record in self.history:
            for added in record.messagesAdded:
                ids[added.message.id] = None
        return list(ids)
