import logging
import uuid

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.jwt import decode
from app.db.session import get_db
from app.middleware.cors import add_cors_middleware
from app.email_service.gmail.router import auth_gmail_router
from app.models.decoded_jwt import DecodedJWT
from app.models.email_account_response import EmailAccountResponse
from app.models.register_user_request import RegisterUserRequest
from app.models.update_user_request import UpdateUserRequest
from app.models.user_response import UserResponse
from app.repositories.category import create_default_categories
from app.repositories.email_account import disconnect_email_account
from app.repositories.email_account import email_account_find_one_by_id
from app.repositories.email_account import email_accounts_find_all_by_user
from app.repositories.user import create_user
from app.repositories.user import delete_user
from app.repositories.user import update_user
from app.repositories.user import user_find_one_by_clerk_id

app = FastAPI()
add_cors_middleware(app)
app.include_router(auth_gmail_router)
logger = logging.getLogger(__name__)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post(
    "/api/users/create",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_endpoint(
    body: RegisterUserRequest,
    decoded_jwt: DecodedJWT = Depends(decode),
    db: Session = Depends(get_db),
):
    try:
        user = create_user(db, decoded_jwt.user_id, body.first_name, body.last_name)
        create_default_categories(db, user.id)
        db.commit()

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="This account already exists.",
        )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create account. Please try again later.",
        )

    return user

@app.get(
    "/api/users/find",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def find_user_endpoint(
    decoded_jwt: DecodedJWT = Depends(decode),
    db: Session = Depends(get_db),
):
    try:
        user = user_find_one_by_clerk_id(db, decoded_jwt.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found. Please create an account first.",
            )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve account. Please try again later.",
        )

    return user

@app.patch(
    "/api/users/update",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
)
def update_user_endpoint(
    body: UpdateUserRequest,
    decoded_jwt: DecodedJWT = Depends(decode),
    db: Session = Depends(get_db),
):
    try:
        user = user_find_one_by_clerk_id(db, decoded_jwt.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found. Please create an account first.",
            )
        
        user = update_user(db, user, body.first_name, body.last_name)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update account. Please try again later.",
        )

    return user

@app.delete(
    "/api/users/delete",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_user_endpoint(
    decoded_jwt: DecodedJWT = Depends(decode),
    db: Session = Depends(get_db),
):
    try:
        user = user_find_one_by_clerk_id(db, decoded_jwt.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found. Please create an account first.",
            )

        delete_user(db, user)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete account. Please try again later.",
        )


@app.get(
    "/api/email-accounts/find-all",
    response_model=list[EmailAccountResponse],
    status_code=status.HTTP_200_OK,
)
def find_all_email_accounts_endpoint(
    decoded_jwt: DecodedJWT = Depends(decode),
    db: Session = Depends(get_db),
):
    try:
        user = user_find_one_by_clerk_id(db, decoded_jwt.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found. Please create an account first.",
            )

        accounts = email_accounts_find_all_by_user(db, user.id)

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve email accounts. Please try again later.",
        )

    return accounts

@app.get(
    "/api/email-accounts/find/{email_account_id}",
    response_model=EmailAccountResponse,
    status_code=status.HTTP_200_OK,
)
def find_email_account_by_id_endpoint(
    email_account_id: uuid.UUID,
    decoded_jwt: DecodedJWT = Depends(decode),
    db: Session = Depends(get_db),
):
    try:
        user = user_find_one_by_clerk_id(db, decoded_jwt.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found. Please create an account first.",
            )

        account = email_account_find_one_by_id(db, email_account_id, user.id)

        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Email account not found.",
            )

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve email account. Please try again later.",
        )

    return account

@app.delete(
    "/api/email-accounts/disconnect/{email_account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def disconnect_email_account_endpoint(
    email_account_id: uuid.UUID,
    decoded_jwt: DecodedJWT = Depends(decode),
    db: Session = Depends(get_db)
):
    try:
        user = user_find_one_by_clerk_id(db, decoded_jwt.user_id)

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Account not found. Please create an account first.",
            )

        account = email_account_find_one_by_id(db, email_account_id, user.id)

        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Gmail account not found.",
            )

        disconnect_email_account(db, account)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to disconnect Gmail. Please try again later.",
        )

# Stats endpoint
@app.get(
    "/api/email-accounts/{email_account_id}/stats/categories",
    status_code=status.HTTP_200_OK,
)
def statsCategories_endpoint():
    return {"Emails grouped by category": "ok"}

@app.get(
    "/api/email-accounts/{email_account_id}/stats/drafts",
    status_code=status.HTTP_200_OK,
)
def emailDrafts_endpoint():
    return {"Emails needing drafts": "ok"}