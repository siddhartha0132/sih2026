"""
Auth: password hashing + JWT issue/verify.

Deliberately simple for a hackathon demo timeline (no refresh tokens, no
email verification, no password-reset flow) but genuinely real: passwords are
bcrypt-hashed, never stored or logged in plaintext, and the session token is a
real signed JWT with an expiry — not a mock.
"""
import datetime
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models_db import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Not marked as required (auto_error=False) so open-use requests without any
# token don't get rejected — they just proceed as an anonymous/open request.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login", auto_error=False)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days — fine for a demo


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.jwt_secret_key, algorithm="HS256")


def _decode_user_id(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        sub = payload.get("sub")
        return int(sub) if sub is not None else None
    except (JWTError, ValueError):
        return None


def get_current_user(
    token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    """Strict dependency — use on routes that REQUIRE a logged-in user (personal-use only)."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception
    user_id = _decode_user_id(token)
    if user_id is None:
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Non-strict dependency — used on /api/advisory so open-use requests (no
    token) work exactly as before, while personal-use requests (with a valid
    token) get their run auto-saved to history.
    """
    if not token:
        return None
    user_id = _decode_user_id(token)
    if user_id is None:
        return None
    return db.query(User).filter(User.id == user_id).first()
