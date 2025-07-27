"""FastAPI dependencies for authentication, rate limiting, and JWT token management.

Must be used alongside core.config for environment-driven settings.
This module centralizes logic for JWT auth, rate limiting, and user management.
"""

from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import logging
from fastapi import Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from passlib.context import CryptContext
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT constants
ALGORITHM = "HS256"
security_scheme = HTTPBearer()

# In-memory demo user — replace with MongoDB user collection in production
fake_user_db = {
    "user": {
        "username": "user",
        "hashed_password": pwd_context.hash("password"),
    }
}

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Securely check if a plain password matches a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def authenticate(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with username and hashed password.
    
    Args:
        username: The user to authenticate.
        password: The plaintext password to check.
    
    Returns:
        The user dict if valid, None otherwise.
    """
    user = fake_user_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        logger.warning("Failed login attempt for username: %s", username)
        return None
    logger.info("Successful login for username: %s", username)
    return user

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT token with the given data and expiry.
    
    Args:
        data: Dict to encode (must include 'sub' for FastAPI users).
        expires_delta: Optional timedelta for token expiry (defaults to settings).
    
    Returns:
        A JWT token string.
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)

# Rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=[settings.RATE_LIMIT])

def init_rate_limiter(app) -> None:
    """Initialize the rate limiter middleware on the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(429, _rate_limit_exceeded_handler)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme)
) -> str:
    """Get the current authenticated user from a JWT in the Authorization header.
    
    Uses the FastAPI HTTPBearer dependency to parse and validate the JWT.
    Checks the JWT's signature, expiry, and required claims.
    Returns the 'sub' (typically username) if valid.
    
    Raises:
        HTTPException: 401 on missing/invalid token, 403 on expired or missing 'sub'.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require_exp": True},
        )
        if "sub" not in payload:
            raise JWTError("Missing required 'sub' claim")
    except JWTError as e:
        logger.error("JWT validation failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return payload["sub"]
