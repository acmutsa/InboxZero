from typing import Optional
from pydantic import BaseModel, EmailStr, TypeAdapter, ValidationError

email = TypeAdapter(EmailStr)

class User(BaseModel):
    id: str
    displayName: Optional[str] = None
    mail: Optional[EmailStr] = None
    userPrincipalName: Optional[EmailStr] = None

    @property
    def email(self) -> Optional[str]:
        return self.mail or self.userPrincipalName

        