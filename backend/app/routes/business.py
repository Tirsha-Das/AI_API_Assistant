# backend/app/routes/business.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models.all_models import Customer, Order, User
from schemas.business import CustomerCreate, CustomerUpdate, CustomerResponse, OrderCreate, OrderResponse
from core.dependencies import get_current_user  # 🛡️ Injected Gatekeeper

router = APIRouter(prefix="/business", tags=["Mock Business Sandbox Data"])


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(data: CustomerCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Creates a new mock customer row. Requires an active logged-in application User session."""
    existing = db.query(Customer).filter(Customer.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer email already exists")
    
    new_customer = Customer(name=data.name, email=data.email)
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer

@router.get("/customers/{id}", response_model=CustomerResponse)
def get_customer(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieves a single business customer profile by database sequence ID."""
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer

@router.put("/customers/{id}", response_model=CustomerResponse)
def update_customer(id: int, data: CustomerUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Modifies mock target parameters for an existing customer resource profile."""
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    if data.name is not None:
        customer.name = data.name
    if data.email is not None:
        email_check = db.query(Customer).filter(Customer.email == data.email, Customer.id != id).first()
        if email_check:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already taken by another customer")
        customer.email = data.email
        
    db.commit()
    db.refresh(customer)
    return customer

@router.delete("/customers/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Removes a customer and completely cascades structural deletes down into their orders."""
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    
    db.delete(customer)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ==========================================
# ORDER ROUTING & RELATION LINKS
# ==========================================

@router.post("/customers/{id}/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(id: int, data: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generates a transactional order entry explicitly mapped to a business customer profile record."""
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        
    new_order = Order(customer_id=id, total_amount=data.total_amount, status=data.status)
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/customers/{id}/orders", response_model=List[OrderResponse])
def get_customer_orders(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Returns a full array summary of orders matching a target business profile link query."""
    customer = db.query(Customer).filter(Customer.id == id).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer.orders
