from typing import Optional
from pydantic import BaseModel

class NotificationResource(BaseModel):
    id: Optional[str] = None

class OutlookNotification(BaseModel):
    subscriptionId: Optional[str] = None
    clientState: Optional[str] = None
    changeType: Optional[str] = None
    resourceData: Optional[NotificationResource] = None #The message IDs

    @property
    def message_id(self) -> Optional[str]:
        return self.resourceData.id if self.resourceData else None

class OutlookNotificationList(BaseModel):
    value: list[OutlookNotification] = []
