# # backend/app/routes/users.py
# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session
# from database import get_db
# from models.all_models import User
# from schemas.user import UserCreate, UserResponse

# router = APIRouter(prefix="/users", tags=["Users"])

# @router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
# def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
#     # Check duplicate email
#     existing_user = db.query(User).filter(User.email == user_data.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Crude plain-text assignment for demo. Replace with passlib hashing in real production.
#     new_user = User(email=user_data.email, hashed_password=user_data.password)
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user

# @router.get("/{user_id}", response_model=UserResponse)
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# backend/app/routes/users.py
from fastapi import APIRouter, Depends
from models.all_models import User
from schemas.user import UserResponse
from core.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/profile", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Protected endpoint that only returns details if a valid Bearer Token is passed."""
    return current_user

