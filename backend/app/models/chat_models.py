from pydantic import BaseModel
from typing import List, Dict, Optional


class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []
    session_id: Optional[int] = None


class RenameChatRequest(BaseModel):
    title: str


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str