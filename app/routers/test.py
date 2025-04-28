# app/routers/test.py

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlmodel import Session, select

from app.db.database import get_session
from app.models.user import User
from app.models.conversation import Conversation
from app.models.message import Message

router = APIRouter()

@router.get("/test/db", response_class=HTMLResponse)
def db_view(
    session: Session = Depends(get_session)
):
    """
    DB 내용(Users, Conversations, Messages)를 HTML로 반환
    """
    users = session.exec(select(User)).all()
    conversations = session.exec(select(Conversation)).all()
    messages = session.exec(select(Message)).all()

    html_content = "<html><body>"
    html_content += "<h1>Database View</h1>"

    # Users
    html_content += "<h2>Users</h2><table border='1'>"
    html_content += "<tr><th>ID</th><th>Username</th><th>Email</th><th>Photo URL</th></tr>"
    for user in users:
        html_content += f"<tr><td>{user.id}</td><td>{user.username}</td><td>{user.email}</td><td>{user.photo_url}</td></tr>"
    html_content += "</table>"

    # Conversations
    html_content += "<h2>Conversations</h2><table border='1'>"
    html_content += "<tr><th>ID</th><th>Owner ID</th><th>Title</th><th>Last Modified</th></tr>"
    for conv in conversations:
        html_content += f"<tr><td>{conv.id}</td><td>{conv.owner_id}</td><td>{conv.title}</td><td>{conv.last_modified}</td></tr>"
    html_content += "</table>"

    # Messages
    html_content += "<h2>Messages</h2><table border='1'>"
    html_content += "<tr><th>ID</th><th>Conversation ID</th><th>Sender</th><th>Content</th></tr>"
    for msg in messages:
        html_content += f"<tr><td>{msg.id}</td><td>{msg.conv_id}</td><td>{msg.sender}</td><td>{msg.content}</td></tr>"
    html_content += "</table>"

    html_content += "</body></html>"

    return HTMLResponse(content=html_content)