# import uvicorn
# from fastapi import FastAPI

# app = FastAPI()

# @app.get("/health")
# def read_root():
#     return {"status": "ok"}

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

# backend/app/main.py
# backend/app/main.py
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import engine, Base, get_db
from models.all_models import User, Conversation, Message
# 1. Import the router you created
from routes import users, auth

# Build tables if they do not exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI API Assistant", description="FastAPI + PostgreSQL Industry Standard Setup")

# 2. Register the router with your FastAPI app instance
app.include_router(users.router)
app.include_router(auth.router)

# Quick verification route
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database down: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
