from datetime import datetime
from datetime import timedelta
from datetime import timezone

from pydantic import BaseModel
from pydantic import Field

INBOX_MESSAGES = "me/mailFolders('inbox')/messages"
SUBSCRIPTION_LIFETIME = timedelta(days=6)

def expires_in_six_days() -> datetime:
    return datetime.now(timezone.utc) + SUBSCRIPTION_LIFETIME

class SubscriptionCreateRequest(BaseModel):
    notificationUrl: str
    clientState: str
    changeType: str = "created"
    resource: str = INBOX_MESSAGES
    expirationDateTime: datetime = Field(default_factory=expires_in_six_days)

class SubscriptionRenewRequest(BaseModel):
    id: str
    expirationDateTime: datetime = Field(default_factory=expires_in_six_days)

class Subscription(BaseModel):
    id: str
    resource: str
    changeType: str
    expirationDateTime: datetime
