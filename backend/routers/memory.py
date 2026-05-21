"""Memory retrieval endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from memory.memory_manager import MemoryManager
import uuid

router  = APIRouter()
manager = MemoryManager()


class SearchRequest(BaseModel):
    user_id: str
    query:   str
    limit:   int = 5


@router.get("/{user_id}/conversations")
async def get_conversations(user_id: str, limit: int = 10):
    """Get recent conversation history for a user."""
    try:
        convs = await manager.get_recent_conversation(
            uuid.UUID(user_id), limit=limit
        )
        return {
            "user_id": user_id,
            "count":   len(convs),
            "conversations": [
                {
                    "role":       c.role,
                    "content":    c.content,
                    "created_at": c.created_at.isoformat(),
                }
                for c in convs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/search")
async def search_memories(request: SearchRequest):
    """Semantic search across user memories."""
    try:
        results = await manager.search_memories_semantic(
            uuid.UUID(request.user_id),
            request.query,
            limit=request.limit
        )
        return {
            "query":   request.query,
            "results": [
                {
                    "content":    m.content,
                    "similarity": round(score, 4),
                    "type":       m.memory_type,
                }
                for m, score in results
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{user_id}/preferences")
async def get_preferences(user_id: str):
    """Get learned user preferences."""
    try:
        prefs = await manager.get_preferences(uuid.UUID(user_id))
        return {
            "user_id":     user_id,
            "preferences": [
                {
                    "content":    p.content,
                    "importance": p.importance,
                }
                for p in prefs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))