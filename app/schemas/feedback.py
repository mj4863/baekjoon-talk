# app/schemas/feedback.py

import datetime as dt
from pydantic import BaseModel, Field

class CodeErrorStats(BaseModel):
    error_type: str = Field(description="코드 오류 종류 (ex. syntax_error)")
    count: int = Field(description="발생 횟수")

class RecommendedTagStats(BaseModel):
    tag: str = Field(description="추천된 문제 태그")
    count: int = Field(description="추천된 횟수")

class RequestTypeDates(BaseModel):
    request_type: str | None = Field(description="요청 종류 (hint, review, complexity, optimize, general(일반적인 대화))")
    dates: list[dt.date] = Field(description="해당 요청 종류가 발생한 날짜 목록")

class UserFeedbackStats(BaseModel):
    code_analysis_requests: list[RequestTypeDates] = Field(description="코드 분석/힌트 요청 종류별 횟수")
    top_code_errors: list[CodeErrorStats] = Field(description="가장 많이 발생한 코드 오류 종류 및 횟수")
    total_logins: int = Field(description="총 접속 횟수")
    average_session_duration_minutes: float = Field(description="평균 접속 시간 (분)")
    top_recommended_tags: list[RecommendedTagStats] = Field(description="가장 많이 추천받은 문제 태그")
    llm_conversation_summary: str | None = Field(None, description="LLM이 생성한 대화 요악/평가 (3줄)")