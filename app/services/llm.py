# app/services/llm.py

from app.core.configuration import settings

async def generate_response(messages: list[dict]) -> str:
    return f"Response From LLM: {messages}"