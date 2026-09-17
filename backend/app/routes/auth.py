# backend/app/routes/auth.py
import logging
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from config import settings
from database import get_db
from models.all_models import User
from schemas.user import UserCreate, UserResponse
from schemas.auth import TokenResponse, RefreshRequest
from core.security import get_password_hash, verify_password, create_token

logger = logging.getLogger("app.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"📥 New account registration request received for email: {user_data.email}")
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"⚠️ Registration rejected: Email '{user_data.email}' already exists in PostgreSQL.")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    logger.info("🎛️  Processing password with the Bcrypt blender...")
    hashed_pass = get_password_hash(user_data.password)
    
    logger.info(f"💾 Saving new user profile with masked string to DB: {hashed_pass[:20]}...")
    new_user = User(email=user_data.email, hashed_password=hashed_pass)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"🎉 Registration successful! Assigned Database User ID: {new_user.id}")
    return new_user

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"🔑 Login request submitted for user: {form_data.username}")
    
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        logger.warning(f"❌ Login failed: User email '{form_data.username}' not found in DB.")
        raise HTTPException(status_code=401, detail="Incorrect email or password")
        
    logger.info("🔬 Fetching stored hash and evaluating plain-text match via Bcrypt...")
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"❌ Login failed: Invalid password string passed for user '{form_data.username}'.")
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    logger.info(f"✅ Credentials match! Manufacturing dual JWT layers for User ID {user.id}...")
    access_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    access_token = create_token(user.id, access_delta, "access")
    refresh_token = create_token(user.id, refresh_delta, "refresh")
    
    logger.info("🎟️  Tokens generated successfully! Handing responses over to client storage.")
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
def refresh_tokens(payload: RefreshRequest, db: Session = Depends(get_db)):
    logger.info("🔄 Token renewal requested! Evaluating Refresh token string...")
    try:
        decoded = jwt.decode(payload.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = decoded.get("sub")
        token_type: str = decoded.get("type")
        
        logger.info(f"📝 Decoded Refresh token -> User ID: {user_id} | Type check: '{token_type}'")
        
        if user_id is None or token_type != "refresh":
            logger.warning("❌ Token renewal failed: Payload layout incorrect or token is not a refresh type.")
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
    except JWTError as e:
        logger.error(f"💥 Refresh validation crash: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid refresh token")
        
    logger.info(f"🎟️  Voucher validated! Minting brand-new access token for User ID {user_id}...")
    access_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    return {
        "access_token": create_token(user_id, access_delta, "access"),
        "refresh_token": create_token(user_id, refresh_delta, "refresh"),
        "token_type": "bearer"
    }
