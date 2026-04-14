from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from Backend.app.core.config import settings
from Backend.app.core.database import get_session
from Backend.app.Schema.schema import User
import hashlib
import base64

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# ── Password ───────────────────────────────────────────────────────────────────

def prehash_password(password:str) -> str:
    return base64.b64encode(hashlib.sha256(password.encode()).digest()).decode()

def hashed_password(password:str) -> str:
    return pwd_context.hash(prehash_password(password))

def verify_password(plain:str, hashed:str) -> bool:
    return pwd_context.verify(prehash_password(plain), hashed)

 
# ── JWT Token ──────────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta]= None)-> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = "Invalid or expired token")
    
# ── Get Current User ───────────────────────────────────────────────────────────

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    payload = decode_token(token)
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = session.get(User, int(user_id))

    if not user:
        raise HTTPException(status_code=403, detail="Account is inactive")
    
    return user

# ── Role Checker ───────────────────────────────────────────────────────────────

def require_role(*roles):
    """
    Usage:
        current_user = Depends(require_role("recruiter", "admin"))
        current_user = Depends(require_role("candidate"))
    """
    def checker(current_user=Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(status_code=403, detail=f"Access denied. Required role: {list(roles)}")
        return current_user
    return checker