# app/crud/message.py

from sqlmodel import select, Session
from app.models.message import Message
from typing import Annotated
from uuid import uuid4

def create_message(
        session: Session,
        conv_id: str,
        sender: str,
        content: str
) -> Message:
    """
    Message 생성
    - Conversation ID (특정 conversation에 종속되어야 함)
    - Sender (User / LLM(bot))
    - Content (메시지 내용)
    """
    message = Message(
        id=str(uuid4()),
        conv_id=conv_id,
        sender=sender,
        content=content
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

def get_message(
        session: Session,
        message_id: str
) -> Message | None:
    """
    Returns Message by Message ID
    """
    statement = select(Message).where(Message.id == message_id)
    result = session.exec(statement)
    return result.first()

def list_messages_by_conversation(
        session: Session,
        conv_id: str
) -> list[Message]:
    """
    Returns All messages of Conversation (conv_id)
    """
    statement = select(Message).where(Message.conv_id == conv_id)
    result = session.exec(statement)
    return result.all()

def delete_messages_by_conversation(
        session: Session,
        conv_id: str
) -> None:
    statement = select(Message).where(Message.conv_id == conv_id)
    messages = session.exec(statement).all()
    for msg in messages:
        session.delete(msg)
    
    session.commit()