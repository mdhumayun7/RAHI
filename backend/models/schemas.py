"""
RAHI Pydantic Models
Centralized request/response models for all endpoints.
"""
from pydantic import BaseModel
from typing import Optional


class CreateUserRequest(BaseModel):
    name:  str
    email: Optional[str] = None


class UserResponse(BaseModel):
    id:    str
    name:  str
    email: Optional[str]


class ChatRequest(BaseModel):
    user_id:    str
    session_id: str
    message:    str


class ChatResponse(BaseModel):
    response:      str
    session_id:    str
    message_count: int


class MemorySearchRequest(BaseModel):
    user_id: str
    query:   str
    limit:   int = 5


class HealthResponse(BaseModel):
    rahi:       str
    postgres:   str
    redis:      str
    embeddings: str
    overall:    str
