import LabelResponse form "./app/email_service/gmail/types/label.py "
class Category:
    def __init__(self):
        self.name = None
    def form_gmail_lable(self, lable:LabelResponse):
        self.name = lable.name  

    