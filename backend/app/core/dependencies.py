# backend/app/core/dependencies.py
import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from config import settings
from database import get_db
from models.all_models import User

logger = logging.getLogger("dependencies")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    logger.info("🛡️  Gatekeeper activated! Intercepting request header to evaluate incoming token...")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Print a short slice of the token to the log so we know what it looks like without filling the console
        logger.info(f"🔑 Received Token: Bearer {token[:15]}...[truncated]")
        
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        logger.info(f"📝 Decoded Payload Data -> User ID: {user_id} | Token Type: '{token_type}'")
        
        if user_id is None or token_type != "access":
            logger.warning(f"❌ Token validation failed: Missing ID or incorrect type. Type found: '{token_type}'")
            raise credentials_exception
            
    except JWTError as e:
        logger.error(f"💥 Cryptographic Signature Verification Error: {str(e)}")
        raise credentials_exception
        
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        logger.warning(f"❌ Database lookup failed: User ID {user_id} no longer exists in PostgreSQL.")
        raise credentials_exception
        
    logger.info(f"✅ Access Granted! User '{user.email}' passed all gatekeeper checks successfully.")
    return user
