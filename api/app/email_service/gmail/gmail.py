
BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"


# GET	/labels	List all labels, both system and user
# GET	/labels/{id}	Get one label, including message and unread counts
# POST	/labels	Create a label
# DELETE	/labels/{id}	Delete a label and remove it from all messages

# POST	/messages/{id}/modify	Add or remove labels on one message
# POST	/threads/{id}/modify	Add or remove labels on every message in a thread
# GET	/messages?labelIds=X	List the messages that have a given label"""HTTP endpoints the frontend uses to connect Gmail and work with email."""


# GET	/drafts	List drafts (IDs only)
# GET	/drafts/{id}?format=full	Get one draft with its message
# POST	/drafts	Create a draft


# GET	/profile	Account email, total messages and threads, current historyId

BASE_URL + "/messages" 

# GET	/messages	List message IDs (with q, labelIds, and pagination, as covered in the inbox answer)
# GET	/messages/{id}?format=...	Get one message
# POST	/messages/send	Send a new email directly, without a draft
# POST	/messages/{id}/modify	Add or remove labels (read/unread, archive, star)

