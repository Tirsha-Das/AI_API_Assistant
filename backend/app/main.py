# backend/app/main.py
import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from models.all_models import User, Conversation, Message
from database import engine,Base, get_db
from routes import auth, users, business, document, rag
from rag.engine import init_qdrant_collection

# Configure logging parameters
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("main")

# 🛰️ 1. Create a safe async lifespan block to handle AI model / memory states
@asynccontextmanager
async def lifespan(app: FastAPI):
    # This runs the moment the server process fully boots
    logger.info("🎬 Initializing application system layers...")
    Base.metadata.create_all(bind=engine)
    init_qdrant_collection() # ◄ Guaranteed to map collection into memory space safely
    yield
    # This runs when the server shuts down (if you need cleanups)
    logger.info("🛑 Shutting down application system layers...")

# 🚀 2. Pass the lifespan context right into the FastAPI app builder
app = FastAPI(
    title="AI API Assistant", 
    description="FastAPI + Local In-Memory Qdrant RAG Infrastructure",
    lifespan=lifespan
)

# Mount all endpoint routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(business.router)
app.include_router(document.router)
app.include_router(rag.router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
