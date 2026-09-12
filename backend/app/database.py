from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from config import settings

DATABASE_URL = str(settings.DATABASE_URL)

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,  # Automatically tests disconnected connections
    pool_size=10,        # Keeps a pool of active DB connections
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
