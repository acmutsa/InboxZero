from fastapi import FastAPI

app = FastAPI()

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
def statsCategories(account_id: str):
    return {"Emails grouped by category": "ok"}

@app.get("/api/accounts/{account_id}/stats/drafts")
def emailDrafts(account_id: str):
    return {"Emails needing drafts": "ok"}