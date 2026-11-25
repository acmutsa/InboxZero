from abc import ABC
from abc import abstractmethod

from app.email_service.types.draft import ReplyDraft
from app.email_service.types.message import EmailMessage
from app.email_service.types.message import EmailThread


class EmailProvider(ABC):
    @abstractmethod
    def get_message(self, message_id: str) -> EmailMessage: ...

    @abstractmethod
    def get_thread(self, thread_id: str) -> EmailThread: ...

    @abstractmethod
    def create_reply_draft(self, original: EmailMessage, reply: ReplyDraft) -> str: ...

    @abstractmethod
    def apply_category(self, message_id: str, category_name: str) -> None: ...
