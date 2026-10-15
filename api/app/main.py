import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.jwt import decode
from app.middleware.cors import add_cors_middleware
from app.email_service.gmail.router import auth_gmail_router

app = FastAPI()
add_cors_middleware(app)
app.include_router(auth_gmail_router)
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