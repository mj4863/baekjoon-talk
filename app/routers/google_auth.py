# app/routers/google_auth.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.configuration import settings
from app.core.security import create_access_token
from app.db import fake_db

router = APIRouter()

class TokenIn(BaseModel):
    id_token: str

@router.post("/verify")
async def verify_id_token(payload: TokenIn):
    """
    Google 인증 방식
    """
    try:
        info = id_token.verify_oauth2_token(
            payload.id_token,
            requests.Request(),
            audience=settings.GOOGLE_CLIENT_ID,
        )
    except ValueError as e:
        raise HTTPException(400, f"Invalid Google ID Token: {e}")
    
    username = info["email"]
    photo = info.get("picture")

    user = fake_db.get_user(username) or fake_db.add_user(username, hashed_password="", photo_url=photo)
    if photo and user.get("photo_url") != photo:
        fake_db.update_user_photo(username, photo)
    
    jwt = create_access_token({"sub": username})
    return {"jwt": jwt, "username": username, "photo_url": photo}