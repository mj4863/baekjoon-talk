# app/dependencies.py

from typing import Annotated
from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.security import decode_access_token
from app.db.database import engine
from app.schemas.user import UserOut
from app.crud import user as crud_user

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        session: Annotated[Session, Depends(get_session)]
) -> UserOut:
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Token"
        )
    email: str = payload.get("sub")
    db_user = crud_user.get_user_by_email(session, email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return UserOut(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        photo_url=db_user.photo_url
    )