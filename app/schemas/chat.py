# app/schemas/chat.py

from typing import Annotated
from pydantic import BaseModel, Field

class ConversationCreate(BaseModel):
    title: str | None = Field(None, example="Daily Chat")

class ConversationOut(BaseModel):
    id: str
    title: str
    last_modified: str # ISO8601

class MessageIn(BaseModel):
    content: Annotated[str, Field(None, example="Hello, how are you?")]
    voice: bytes | None = None

class MessageOut(BaseModel):
    id: str
    sender: str
    content: str
    audio_base64: str | None = None

class ConversationOutWithFirstMessage(BaseModel):
    id: str
    title: str
    last_modified: str
    first_message: MessageOut