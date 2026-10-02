from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.email_service.gmail.config import get_settings
from app.email_service.gmail.auth_router import router as gmail_auth_router
from app.email_service.gmail.router import email_service_error_handler, router as gmail_router
from app.email_service.gmail.types.error import EmailServiceError

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(EmailServiceError, email_service_error_handler)
app.include_router(gmail_auth_router)
app.include_router(gmail_router)

@app.get("/health")
def health():
    return {"status": "ok"}
