
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.email_service.outlook.outlook import OutlookService
from fastapi import Response, status

from app.email_service.outlook.types.draft import DraftRequest
from app.email_service.outlook.types.message import (
    MessageRequest,
    MessageModifyRequest,
)
from app.email_service.outlook.types.label import LabelRequest

# Development-only dependency.
# Replace with a database-backed, authenticated dependency
# before registering this router in the main application.
def get_outlook_service():
    raise HTTPException(
        status_code=503,
        detail="Outlook account integration is not configured",
    )


outlook_email_router = APIRouter(
    prefix="/api/outlook",
    tags=["outlook-email"],
)


class OutlookMessageUpdate(BaseModel):
    is_read: bool


@outlook_email_router.get("/profile")
def get_profile(service: OutlookService = Depends(get_outlook_service)):
    return service.get_profile()


@outlook_email_router.get("/messages")
def get_messages(service: OutlookService = Depends(get_outlook_service)):
    return service.get_messages()


@outlook_email_router.get("/messages/{message_id}")
def get_message(
    message_id: str,
    service: OutlookService = Depends(get_outlook_service),
):
    return service.get_message(message_id)


@outlook_email_router.get("/drafts")
def get_drafts(service: OutlookService = Depends(get_outlook_service)):
    return service.get_drafts()


@outlook_email_router.get("/drafts/{draft_id}")
def get_draft(
    draft_id: str,
    service: OutlookService = Depends(get_outlook_service),
):
    return service.get_draft(draft_id)

# -----------------------------
# Draft operations
# -----------------------------

@outlook_email_router.post(
    "/drafts",
    status_code=status.HTTP_201_CREATED,
)
def create_draft(
    draft: DraftRequest,
    service: OutlookService = Depends(get_outlook_service),
):
    return service.create_draft(draft)


@outlook_email_router.post(
    "/drafts/{draft_id}/send",
    status_code=status.HTTP_204_NO_CONTENT,
)
def send_draft(
    draft_id: str,
    service: OutlookService = Depends(get_outlook_service),
):
    service.send_draft(draft_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# -----------------------------
# Message operations
# -----------------------------

@outlook_email_router.post(
    "/messages/send",
    status_code=status.HTTP_204_NO_CONTENT,
)
def send_message(
    message: MessageRequest,
    service: OutlookService = Depends(get_outlook_service),
):
    service.send_message(message)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@outlook_email_router.patch("/messages/{message_id}")
def modify_message(
    message_id: str,
    modification: MessageModifyRequest,
    service: OutlookService = Depends(get_outlook_service),
):
    return service.modify_message(message_id, modification)


# -----------------------------
# Outlook categories
# -----------------------------

@outlook_email_router.get("/categories")
def get_categories(
    service: OutlookService = Depends(get_outlook_service),
):
    return service.get_labels()


@outlook_email_router.post(
    "/categories",
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    label: LabelRequest,
    service: OutlookService = Depends(get_outlook_service),
):
    return service.create_label(label)
