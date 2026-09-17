# backend/app/main.py
import logging
import uvicorn
from fastapi import FastAPI
from database import engine, Base, get_db
from models.all_models import User, Conversation, Message
from routes import auth, users, business

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("app.main")

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI API Assistant")

logger.info("🚀 Database synchronized and FastAPI application started successfully!")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(business.router)

@app.get("/health")
def health_check():
    return "Success"

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
