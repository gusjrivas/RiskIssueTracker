from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserResponse
from app.services.auth_service import (
    authenticate_password,
    create_access_token,
    get_current_user,
    register_with_password,
)
from app.schemas.common import UserStatus

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    user = register_with_password(db, body.email, body.password, body.full_name)
    return user


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    from sqlalchemy import select
    from app.schemas.common import UserStatus

    user = authenticate_password(db, body.email, body.password)
    if user is None:
        # Check if the user exists but is pending/inactive to give the right error
        from app.models.user import User as UserModel
        existing = db.execute(select(UserModel).where(UserModel.email == body.email)).scalar_one_or_none()
        if existing and existing.status == UserStatus.pending:
            raise HTTPException(status_code=403, detail="Account pending approval")
        if existing and existing.status == UserStatus.inactive:
            raise HTTPException(status_code=403, detail="Account deactivated")
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(user))


@router.get("/me", response_model=UserResponse)
def me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user
