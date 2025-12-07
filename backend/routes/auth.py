"""
Authentication routes
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import logging

from models import UserRegister, UserLogin, Token, User
from database import get_db_connection
from config import settings

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Dependency to get current authenticated user"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = %s AND is_active = TRUE", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def require_admin(user: dict = Depends(get_current_user)) -> dict:
    """Dependency to require admin role"""
    if user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Admin access required")
    return user


@router.post("/register", response_model=Token)
async def register(user_data: UserRegister):
    """Register a new user"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create user
        hashed_password = hash_password(user_data.password)
        cursor.execute("""
            INSERT INTO users (email, password_hash, full_name, role)
            VALUES (%s, %s, %s, 'user')
        """, (user_data.email, hashed_password, user_data.full_name))
        conn.commit()
        
        user_id = cursor.lastrowid
        
        # Create token
        access_token = create_access_token({"sub": str(user_id), "email": user_data.email})
        
        logger.info(f"User registered: {user_data.email}")
        return Token(access_token=access_token)
        
    finally:
        cursor.close()
        conn.close()


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT * FROM users WHERE email = %s", (credentials.email,))
        user = cursor.fetchone()
        
        if not user or not verify_password(credentials.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user['is_active']:
            raise HTTPException(status_code=403, detail="Account is inactive")
        
        # Update last login
        cursor.execute("UPDATE users SET last_login = NOW() WHERE id = %s", (user['id'],))
        conn.commit()
        
        # Create token
        access_token = create_access_token({"sub": str(user['id']), "email": user['email']})
        
        logger.info(f"User logged in: {credentials.email}")
        return Token(access_token=access_token)
        
    finally:
        cursor.close()
        conn.close()


@router.get("/me", response_model=User)
async def get_me(user: dict = Depends(get_current_user)):
    """Get current user info"""
    return User(
        id=user['id'],
        email=user['email'],
        role=user['role'],
        is_active=user['is_active'],
        created_at=user['created_at']
    )
