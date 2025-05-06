# app/routers/chat.py

import os, base64

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlmodel import Session

from app.schemas.chat import ConversationOutWithFirstMessage, ConversationOut, MessageIn, MessageOut
from app.schemas.user import UserOut
from app.dependencies import get_current_user, get_session
from app.crud import message as crud_message
from app.crud import conversation as crud_conversation
from app.services import stt, llm, tts

router = APIRouter()

@router.get("/conversations", response_model=list[ConversationOut])
async def list_conversation(
    session: Session = Depends(get_session),
    user = Depends(get_current_user)
):
    """
    현재 user의 모든 대화 목록 가져오기
    """
    conversations = crud_conversation.list_user_conversation(session, user.id)

    if not conversations:
        raise HTTPException(status_code=404, detail=f"Conversations not found")

    return conversations


@router.get("/conversations/{conv_id}", response_model=ConversationOut)
async def get_conversation(
    conv_id: str,
    session: Annotated[Session, Depends(get_session)],
    user: Annotated[UserOut, Depends(get_current_user)]
):
    """
    특정 대화 세션을 조회
    """
    conversation = crud_conversation.get_conversation(session, conv_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if conversation.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    return ConversationOut(
        id=conversation.id,
        title=conversation.title,
        last_modified=conversation.last_modified
    )


@router.post("/conversations", response_model=ConversationOut, status_code=status.HTTP_201_CREATED)
async def start_conversation(
    msg_in: MessageIn,
    session: Annotated[Session, Depends(get_session)],
    user: Annotated[UserOut, Depends(get_current_user)],
    background_tasks: BackgroundTasks
):
    """
    새로운 대화 세션 생성
    """
    title = "Untitled"

    conversation = crud_conversation.create_conversation(session, owner_id=user.id, title=title)
    # content = msg_in.content if not msg_in.voice else stt.transcribe(msg_in.voice)

    if msg_in.voice:
        content = stt.transcribe_audio(msg_in.voice)
        voice_input = True
    else:
        content = msg_in.content
        voice_input = False

    first_message = crud_message.create_message(
        session=session,
        conv_id=conversation.id,
        sender=user.username,
        content=content
    )

    # LLM 답변
    assistant_response = await llm.generate_response([{"role": "user", "content": content}])

    # Assistant(bot) Message 저장
    assistant_message = crud_message.create_message(
        session=session,
        conv_id=conversation.id,
        sender="assistant",
        content=assistant_response
    )

    crud_conversation.update_last_modified(session, conversation.id)

    # TTS
    audio_base64 = None

    if voice_input:
        tts_file_path = tts.generate_speech(assistant_response)

        # Base64 인코딩
        with open(tts_file_path, "rb") as f:
            audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        background_tasks.add_task(os.remove, tts_file_path)

    return ConversationOutWithFirstMessage(
        id=conversation.id,
        title=conversation.title,
        last_modified=conversation.last_modified,
        first_message=MessageOut(
            id=first_message.id,
            sender=first_message.sender,
            content=first_message.content,
            audio_base64=audio_base64,
        )
    )


@router.get("/conversations/{conv_id}/messages", response_model=list[MessageOut])
async def list_messages(
    conv_id: str,
    session: Annotated[Session, Depends(get_session)],
    user: Annotated[UserOut, Depends(get_current_user)]
):
    """
    특정 대화에 포함된 모든 Message 조회
    """
    conversation = crud_conversation.get_conversation(session, conv_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    messages = crud_message.list_messages_by_conversation(session, conv_id)
    return [MessageOut(id=m.id, sender=m.sender, content=m.content) for m in messages]

@router.post("/conversations/{conv_id}/messages", response_model=MessageOut)
async def post_message(
    conv_id: str,
    msg_in: MessageIn,
    session: Annotated[Session, Depends(get_session)],
    user: Annotated[UserOut, Depends(get_current_user)],
    background_tasks: BackgroundTasks
):
    """
    기존 대화에 메시지를 추가하고, LLM으로부터 답변을 받아 저장
    """
    conversation = crud_conversation.get_conversation(session, conv_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # 음성 입력이 있으면 STT로 변환한다.
    # content = msg_in.content if not msg_in.voice else stt.transcribe(msg_in.voice)

    if msg_in.voice:
        content = stt.transcribe_audio(msg_in.voice)
        voice_input = True
    else:
        content = msg_in.content
        voice_input = False

    # User의 message 저장
    user_message = crud_message.create_message(
        session,
        conv_id=conv_id,
        sender=user.username,
        content=content
    )

    # 대화의 기존 메시지 가져오기 (user/assistant 역할 기반)
    messages = crud_message.list_messages_by_conversation(session, conv_id)
    history = [
        {
            "role": "user" if m.sender == user.username else "assistant",
            "content": m.content
        }
        for m in messages
    ]

    # LLM 호출 후 response 생성
    assistant_response = await llm.generate_response(history)

    # Assistant(bot) Message 저장
    assistant_message = crud_message.create_message(
        session=session,
        conv_id=conv_id,
        sender="assistant",
        content=assistant_response
    )

    # 대화방 마지막 수정시간 갱신
    crud_conversation.update_last_modified(session, conv_id)

    # TTS
    audio_base64 = None

    if voice_input:
        tts_file_path = tts.generate_speech(assistant_response)

        with open(tts_file_path, "rb") as f:
            audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        background_tasks.add_task(os.remove, tts_file_path)

    return MessageOut(
        id=assistant_message.id,
        sender=assistant_message.sender,
        content=assistant_message.content,
        audio_base64=audio_base64,
    )

@router.delete("/conversations/{conv_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conv_id: str,
    session: Session = Depends(get_session),
    user = Depends(get_current_user)
):
    """
    Conversation과 대화 내부의 모든 message 삭제
    """
    conversation = crud_conversation.get_conversation(session, conv_id)

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Message 삭제
    crud_message.delete_messages_by_conversation(session, conv_id)

    # Conversation 삭제
    crud_conversation.delete_conversation(session, conv_id)

    return JSONResponse(
        status_code=200,
        content={
            "detail": "Conversation/Messages have successfully deleted."
        }
    )