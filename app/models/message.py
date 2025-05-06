# app/models/message.py

from sqlmodel import SQLModel, Field
from typing import Annotated
from uuid import uuid4

class Message(SQLModel, table=True):
    __tablename__ = "message"

    id: Annotated[str, Field(default_factory=lambda: str(uuid4()), primary_key=True)]
    conv_id: str
    sender: str
    content: str