from abc import ABC, abstractmethod

class EmailService(ABC):

    # Profile
    @abstractmethod
    def get_profile(self):

    # Labels
    @abstractmethod
    def get_labels(self) :

    @abstractmethod
    def get_label(self) :

    @abstractmethod
    def create_label(self):

    @abstractmethod
    def delete_label(self) :

    # Messages
    @abstractmethod
    def get_messages(self) :

    @abstractmethod
    def get_message(self):

    @abstractmethod
    def modify_message(self) :

    # Threads
    @abstractmethod
    def modify_thread(self) :

    # Drafts
    @abstractmethod
    def get_drafts(self):

    @abstractmethod
    def get_draft(self) 

    @abstractmethod
    def create_draft(self): 
