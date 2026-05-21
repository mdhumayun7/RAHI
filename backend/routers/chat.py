"""
RAHI Chat Endpoint
===================
POST /chat — Send a message, get RAHI's response.

This is where everything connects:
  ReAct Engine + Memory System + Working Memory
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from memory.memory_manager import MemoryManager
from memory.working_memory import WorkingMemory
from brain.react_engine import ReActEngine
import uuid

router  = APIRouter()
manager = MemoryManager()
wm      = WorkingMemory()
engine  = ReActEngine(max_steps=6, verbose=False)  # Silent in API mode


class ChatRequest(BaseModel):
    user_id:    str
    session_id: str
    message:    str


class ChatResponse(BaseModel):
    response:    str
    session_id:  str
    message_count: int


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message to RAHI and get a response.

    Flow:
    1. Save user message to working memory (Redis)
    2. Save to episodic memory (PostgreSQL)
    3. Run ReAct engine to get response
    4. Save response to both memories
    5. Return response
    """
    try:
        user_id    = uuid.UUID(request.user_id)
        session_id = request.session_id
        message    = request.message

        # 1. Add to working memory
        wm.add_message(session_id, "user", message)

        # 2. Save to episodic memory
        await manager.save_conversation(user_id, "user", message)

        # 3. Get conversation context for ReAct
        context = wm.get_context_string(session_id)

        # 4. Build goal with context
        goal = f"""Conversation so far:
{context}

Current user message: {message}

Respond helpfully to the user's message."""

        # 5. Run ReAct engine
        response = engine.run(goal)

        # 6. Save response to memories
        wm.add_message(session_id, "assistant", response)
        await manager.save_conversation(user_id, "assistant", response)

        # 7. Log the interaction
        await manager.log_action(
            action="chat_response",
            user_id=user_id,
            agent="react_engine",
            payload={"message": message[:100]},
            result=response[:100],
        )

        return ChatResponse(
            response=response,
            session_id=session_id,
            message_count=wm.get_message_count(session_id),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAHI error: {str(e)}")


@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get current session context from working memory."""
    messages = wm.get_messages(session_id)
    return {
        "session_id": session_id,
        "message_count": len(messages),
        "messages": messages,
    }


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear session context (start fresh conversation)."""
    wm.clear_session(session_id)
    return {"message": "Session cleared", "session_id": session_id}