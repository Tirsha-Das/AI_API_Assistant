# backend/app/core/security.py
from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import jwt
from passlib.context import CryptContext
from app.config import settings

# Initialize password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies that a plain text password matches its stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a secure cryptographical bcrypt hash from a plain text password."""
    return pwd_context.hash(password)

def create_token(subject: Union[str, Any], expires_delta: timedelta, token_type: str = "access") -> str:
    """Encodes a JSON Web Token (JWT) with an absolute expiration timestamp and token type constraint."""
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire, 
        "sub": str(subject),
        "type": token_type
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
