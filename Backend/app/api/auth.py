from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from Backend.app.core.database import get_session
from Backend.app.core.security import (hashed_password, verify_password, create_access_token, get_current_user)
from Backend.app.Models.models import RegisterRequest, LoginResponse, UserOut
from Backend.app.Schema.schema import User
from Backend.app.core.genericdal import GenericDal

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# ── Register ───────────────────────────────────────────────────────────────────

@router.post("/register", response_model=UserOut)
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    dal = GenericDal(User, session)

    # Check if email already exists
    existing = session.exec(select(User).where(User.email == data.email)).first()

    if existing:
        raise HTTPException(status_code=400, detail="Email already registered. Please login.")
    
    # Create new user 

    user = User(name=data.name, email=data.email, phone=data.phone, hashed_password=hashed_password(data.password), role=data.role,)
    return dal.create(user)

# ── Login ──────────────────────────────────────────────────────────────────────

@router.post("/login", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    dal = GenericDal(User, session)

    # Find user by email using GenericDal
    user = dal.get_by_field("email", form.username)

    # Validate user and password

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Your account has been deactivated")
    
    # Create JWT token
    token = create_access_token({"sub":str(user.id), "role":user.role, "name":user.name})

    return LoginResponse(access_token=token, user_id=user.id, name=user.name, role=user.role, email=user.email)

# ── Get Current User (Me) ──────────────────────────────────────────────────────

@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

# ── Get All Users (Admin only) ─────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
def get_all_users(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):

    if current_user.role != "admin":
        raise HTTPException (status_code=403, detail="Admin only")

    dal = GenericDal(User, session)
    return dal.get_all()
    
    
    









    
