# backend/app/schemas/business.py
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

# --- ORDER SCHEMAS ---
class OrderCreate(BaseModel):
    total_amount: float
    status: Optional[str] = "pending"

class OrderResponse(BaseModel):
    id: int
    customer_id: int
    total_amount: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- CUSTOMER SCHEMAS ---
class CustomerCreate(BaseModel):
    name: str
    email: EmailStr

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None

class CustomerResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True
