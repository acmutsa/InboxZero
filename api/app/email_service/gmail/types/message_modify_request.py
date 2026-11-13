from pydantic import BaseModel

class MessageModifyRequest(BaseModel):
    id: str
    addLabelIds: list[str] = []
    removeLabelIds: list[str] = []
