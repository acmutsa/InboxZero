
from abc import ABC, abstractmethod


class EmailService(ABC):

    # Profile
    @abstractmethod
    def get_profile(self):
        pass

    # Labels
    @abstractmethod
    def get_labels(self):
        pass

    @abstractmethod
    def get_label(self):
        pass

    @abstractmethod
    def create_label(self):
        pass

    @abstractmethod
    def delete_label(self):
        pass

    # Messages
    @abstractmethod
    def get_messages(self):
        pass

    @abstractmethod
    def get_message(self):
        pass

    @abstractmethod
    def modify_message(self):
        pass

    # Threads
    @abstractmethod
    def modify_thread(self):
        pass

    # Drafts
    @abstractmethod
    def get_drafts(self):
        pass

    @abstractmethod
    def get_draft(self):
        pass

    @abstractmethod
    def create_draft(self):
        pass
