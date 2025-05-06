# app/models/user.py

from sqlmodel import SQLModel, Field
from typing import Annotated
from uuid import uuid4

class User(SQLModel, table=True):
    __tablename__ = "user"

    id: Annotated[str, Field(default_factory=lambda: str(uuid4()), primary_key=True)]
    username: str
    email: str
    hashed_password: str
    photo_url: str | None = None