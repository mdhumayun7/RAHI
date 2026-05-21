"""
RAHI Working Memory — Redis Based
===================================
Working memory = current conversation context.

Why Redis?
  - Sub-millisecond read/write
  - Automatic expiry (session ends → memory clears)
  - Perfect for temporary, fast-access data

Use cases:
  - Current conversation window (last N messages)
  - Active task state
  - User session data
"""

import json
import redis
import os
from dotenv import load_dotenv
from datetime import datetime, timezone

load_dotenv()

REDIS_URL  = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SESSION_TTL = 3600   # 1 hour — session expires after this


class WorkingMemory:

    def __init__(self):
        self.client = redis.from_url(REDIS_URL, decode_responses=True)

    # ── Session Management ────────────────────────────────────────────────────

    def ping(self) -> bool:
        """Check if Redis is reachable."""
        try:
            return self.client.ping()
        except Exception:
            return False

    def clear_session(self, session_id: str):
        """Clear all data for a session."""
        keys = self.client.keys(f"session:{session_id}:*")
        if keys:
            self.client.delete(*keys)

    # ── Conversation Context ──────────────────────────────────────────────────

    def add_message(self, session_id: str, role: str, content: str):
        """
        Add a message to the current session's context window.
        Automatically keeps only last 20 messages.
        """
        key = f"session:{session_id}:messages"

        message = json.dumps({
            "role":      role,
            "content":   content,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })

        self.client.rpush(key, message)        # Add to end of list
        self.client.ltrim(key, -20, -1)        # Keep only last 20
        self.client.expire(key, SESSION_TTL)   # Reset expiry

    def get_messages(self, session_id: str) -> list[dict]:
        """Get all messages in current session context."""
        key = f"session:{session_id}:messages"
        raw = self.client.lrange(key, 0, -1)
        return [json.loads(m) for m in raw]

    def get_context_string(self, session_id: str) -> str:
        """
        Format conversation history as a string for LLM prompt.
        Returns: "User: ...\nAssistant: ...\nUser: ..."
        """
        messages = self.get_messages(session_id)
        lines = []
        for msg in messages:
            role = msg["role"].capitalize()
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    # ── Active Task State ─────────────────────────────────────────────────────

    def set_task_state(self, session_id: str, state: dict):
        """Store current ReAct task state (for multi-turn tasks)."""
        key = f"session:{session_id}:task_state"
        self.client.setex(key, SESSION_TTL, json.dumps(state))

    def get_task_state(self, session_id: str) -> dict | None:
        """Retrieve current task state."""
        key = f"session:{session_id}:task_state"
        raw = self.client.get(key)
        return json.loads(raw) if raw else None

    def clear_task_state(self, session_id: str):
        """Clear task state when task is complete."""
        self.client.delete(f"session:{session_id}:task_state")

    # ── User Session Info ─────────────────────────────────────────────────────

    def set_user_session(self, session_id: str, user_id: str, name: str):
        """Store basic user info for this session."""
        key = f"session:{session_id}:user"
        self.client.setex(key, SESSION_TTL, json.dumps({
            "user_id": user_id,
            "name":    name,
        }))

    def get_user_session(self, session_id: str) -> dict | None:
        """Get user info for this session."""
        key = f"session:{session_id}:user"
        raw = self.client.get(key)
        return json.loads(raw) if raw else None

    def get_message_count(self, session_id: str) -> int:
        """How many messages in current session."""
        return self.client.llen(f"session:{session_id}:messages")