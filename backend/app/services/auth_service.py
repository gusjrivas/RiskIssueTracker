from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.common import UserRole, UserStatus, UserTheme

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_bearer = HTTPBearer(auto_error=False)


# ---------------------------------------------------------------------------
# Password helpers
# ---------------------------------------------------------------------------

def hash_password(plain: str) -> str:
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(plain, hashed)


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(user: User) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth_token_expire_minutes)
    payload = {
        "sub": str(user.id),
        "role": user.role.value,
        "exp": expire,
    }
    return jwt.encode(payload, settings.auth_secret_key, algorithm=settings.auth_algorithm)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.auth_secret_key, algorithms=[settings.auth_algorithm])
        if "sub" not in payload:
            raise HTTPException(status_code=401, detail="Token inválido")
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")


# ---------------------------------------------------------------------------
# User operations
# ---------------------------------------------------------------------------

def register_with_password(db: Session, email: str, password: str, full_name: str) -> User:
    existing = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    user = User(
        email=email,
        full_name=full_name,
        password_hash=hash_password(password),
        role=UserRole.user,
        status=UserStatus.pending,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_password(db: Session, email: str, password: str) -> User | None:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        return None
    if not user.password_hash or not verify_password(password, user.password_hash):
        return None
    if user.status != UserStatus.active:
        return None
    return user


# ---------------------------------------------------------------------------
# FastAPI dependencies
# ---------------------------------------------------------------------------

def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Session = Depends(get_db),
) -> User:
    import uuid as _uuid
    if credentials is None:
        raise HTTPException(status_code=401, detail="No autenticado")
    payload = decode_token(credentials.credentials)
    try:
        user_id = _uuid.UUID(payload["sub"])
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    return user


def require_admin(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Se requieren permisos de administrador")
    return current_user


# ---------------------------------------------------------------------------
# Profile operations
# ---------------------------------------------------------------------------

def change_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not user.password_hash:
        raise HTTPException(status_code=400, detail="La cuenta no tiene contraseña (autenticación vía Google)")
    if not verify_password(current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    user.password_hash = hash_password(new_password)
    db.commit()


def update_theme(db: Session, user: User, theme: UserTheme) -> User:
    user.theme = theme
    db.commit()
    db.refresh(user)
    return user
