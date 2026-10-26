import logging

from fastapi import Depends
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import status
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.exc import IntegrityError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.jwt import decode
from app.db.session import get_db
from app.middleware.cors import add_cors_middleware
from app.email_service.gmail.router import auth_gmail_router
from app.models.decoded_jwt import DecodedJWT
from app.models.register_user_request import RegisterUserRequest
from app.models.user_response import UserResponse
from app.repositories.category import create_default_categories
from app.repositories.user import create_user

from contextlib import asynccontextmanager
from arq import create_pool
from pydantic import BaseModel
from app.queue.redis import get_redis_settings


logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = await create_pool(get_redis_settings())
    app.state.redis = redis

    logger.info("Connected to Redis")

    try:
        yield
    finally:
        await redis.aclose()
        logger.info("Disconnected from Redis")


app = FastAPI(lifespan=lifespan)
add_cors_middleware(app)
app.include_router(auth_gmail_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post(
    "/api/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
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

# @app.get("/api/users/find")
# def findProfile():
#     return {"Current user": "profile"}

# # Email account endpoints
# @app.get("/api/accounts")
# def emailList():
#     return {"Email list status": "ok"}

# @app.delete("/api/accounts/{account_id}")
# def deleteAccount(account_id: str):
#     return {"Account deleted": account_id}

# # Stats endpoint
# @app.get("/api/accounts/{account_id}/stats/categories")
# def statsCategories():
#     return {"Emails grouped by category": "ok"}

# @app.get("/api/accounts/{account_id}/stats/drafts")
# def emailDrafts():
#     return {"Emails needing drafts": "ok"}


class TestJobRequest(BaseModel):
    name: str

class IdempotencyTestRequest(BaseModel):
    message_id: str
    name: str

@app.post("/api/queue/test")
async def enqueue_test_job(payload: TestJobRequest, request: Request):
    job = await request.app.state.redis.enqueue_job(
        "test_job",
        payload.name
    )

    if job is None:
        return {"status": "already_enqueued"}

    return {
        "status": "enqueued",
        "job_id": job.job_id
    }

@app.post("/api/queue/retry-test")
async def enqueue_retry_test(payload: TestJobRequest, request: Request):
    job = await request.app.state.redis.enqueue_job(
        "retry_test_job",
        payload.name
    )

    if job is None:
        return {"status": "already_enqueued"}

    return {
        "status": "enqueued",
        "job_id": job.job_id
    }

@app.post("/api/queue/idempotency-test")
async def enqueue_idempotency_test(
    payload: IdempotencyTestRequest,
    request: Request
):
    job_id = f"email:{payload.message_id}"
    
    job = await request.app.state.redis.enqueue_job(
        "retry_test_job",
        payload.name,
        _job_id=job_id
    )

    if job is None:
        return {
            "status": "already_enqueued",
            "job_id": job_id
        }

    return {
        "status": "enqueued",
        "job_id": job.job_id
    }


@app.post("/api/queue/dead-letter-test")
async def enqueue_dead_letter_test(
    payload: TestJobRequest,
    request: Request
):
    job = await request.app.state.redis.enqueue_job(
        "dead_letter_test_job",
        payload.name
    )

    if job is None:
        return {"status": "already_enqueued"}

    return {
        "status": "enqueued",
        "job_id": job.job_id
    }

# @app.delete(
#     "/disconnect-gmail/{user_id}",
#     status_code=status.HTTP_204_NO_CONTENT,
# )
# def disconnect_email(
#     user_id: int,
#     decoded_jwt: DecodedJWT = Depends(decode),
#     db: Session = Depends(get_db)
# ):
#     user_id = decoded_jwt.user_id

#     try:
#         pass
#         #db connection and retrieval logic here
#     except SQLAlchemyError:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve Gmail account. Please try again later.",
#         )
#     if account is None or account.user_id != user_id:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Gmail account not found.",
#         )

#     try:
#         pass
#         # db connection and deletion logic here
#     except SQLAlchemyError:
#         db.rollback()
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to disconnect Gmail. Please try again later.",
#         )