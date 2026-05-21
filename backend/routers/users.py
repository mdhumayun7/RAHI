"""User management endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from memory.memory_manager import MemoryManager
import uuid

router  = APIRouter()
manager = MemoryManager()


class CreateUserRequest(BaseModel):
    name:  str
    email: str | None = None


class UserResponse(BaseModel):
    id:    str
    name:  str
    email: str | None


@router.post("", response_model=UserResponse)
async def create_user(request: CreateUserRequest):
    """Create a new RAHI user."""
    try:
        user = await manager.create_user(
            name=request.name,
            email=request.email
        )
        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str):
    """Get user by ID."""
    try:
        user = await manager.get_user(uuid.UUID(user_id))
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserResponse(
            id=str(user.id),
            name=user.name,
            email=user.email
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")