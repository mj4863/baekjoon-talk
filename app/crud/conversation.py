# app/crud/conversation.py

from sqlmodel import select, Session
from app.models.conversation import Conversation
from typing import Annotated
from uuid import uuid4
import datetime as dt

def create_conversation(
        session: Session,
        owner_id: str,
        title: str
) -> Conversation:
    """
    Conversation 생성
    - 소유자 (User)
    - Title (대화 제목. 대화의 첫번째 질의로 변경하도록 구현하기)
    """
    now = dt.datetime.now().isoformat()
    conversation = Conversation(
        id=str(uuid4()),
        owner_id=owner_id,
        title=title,
        last_modified=now,
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation

def get_conversation(
        session: Session,
        conversation_id: str
) -> Conversation | None:
    """
    Conversation ID로 대화를 찾아 반환하기 (Conversation)
    """
    statement = select(Conversation).where(Conversation.id == conversation_id)
    result = session.exec(statement)
    return result.first()

def update_last_modified(
        session: Session,
        conversation_id: str
) -> Conversation | None:
    """
    Update Last Modified Date-Time
    대화에 메시지가 추가될 때마다 호출하기
    """
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.last_modified = dt.datetime.now().isoformat()
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
    return conversation

def list_user_conversation(
        session:Session,
        owner_id: str
) -> list[Conversation]:
    """
    Returns All Conversations (of a user)
    """
    statement = select(Conversation).where(Conversation.owner_id == owner_id).order_by(Conversation.last_modified.desc())
    result = session.exec(statement)
    return result.all()

def delete_conversation(
        session: Session,
        conv_id: str
) -> None:
    conversation = session.get(Conversation, conv_id)
    if conversation:
        session.delete(conversation)
        session.commit()