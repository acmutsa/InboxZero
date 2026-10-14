from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.email_service.gmail.config import get_settings
from app.email_service.gmail.auth_router import router as gmail_auth_router
from app.email_service.gmail.router import email_service_error_handler, router as gmail_router
from app.email_service.gmail.types.error import EmailServiceError

from src.auth.jwt import decode_access_token
from src.middleware.cors import add_cors_middleware

from app.gnail.router import router as auth_gmail_router

app = FastAPI()
add_cors_middleware(app)
app.include_router(auth_gmail_router, prefix="/auth/google")
logger = logging.getLogger(__name__)

@app.get("/health")
def health():
    return {"status": "ok"}

# Registration endpoints
@app.post("/api/users/register")
def register():
    return {"Status": "success"}

@app.get("/api/users/find")
def findProfile():
    return {"Current user": "profile"}

# Email account endpoints
@app.get("/api/accounts")
def emailList():
    return {"Email list status": "ok"}

@app.delete("/api/accounts/{account_id}")
def deleteAccount(account_id: str):
    return {"Account deleted": account_id}

# Stats endpoint
@app.get("/api/accounts/{account_id}/stats/categories")
def statsCategories():
    return {"Emails grouped by category": "ok"}

@app.get("/api/accounts/{account_id}/stats/drafts")
def emailDrafts():
    return {"Emails needing drafts": "ok"}