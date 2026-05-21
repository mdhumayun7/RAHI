"""
RAHI Memory Manager
====================
High-level interface for all memory operations.

Usage:
    manager = MemoryManager()

    # Store a conversation turn
    await manager.save_conversation(user_id, "user", "My name is Humayun")

    # Store a fact about the user
    await manager.save_memory(user_id, "User's name is Humayun, studies at SVNIT Surat")

    # Retrieve recent conversation
    history = await manager.get_recent_conversation(user_id, limit=10)

    # Search memories semantically
    results = await manager.search_memories(user_id, "where does the user study?")
"""

import uuid
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from memory.models import User, Conversation, Memory, AuditLog
from memory.database import AsyncSessionLocal


class MemoryManager:

    # ── User Operations ──────────────────────────────────────────────────────

    async def create_user(self, name: str, email: str = None) -> User:
        """Create a new user in the database."""
        async with AsyncSessionLocal() as session:
            user = User(name=name, email=email)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"✅ User created: {user.name} (id: {user.id})")
            return user

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        """Fetch a user by ID."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            return result.scalar_one_or_none()

    # ── Conversation (Episodic Memory) ───────────────────────────────────────

    async def save_conversation(
        self,
        user_id: uuid.UUID,
        role: str,
        content: str,
        metadata: dict = None
    ) -> Conversation:
        """Save a single conversation turn."""
        async with AsyncSessionLocal() as session:
            conv = Conversation(
                user_id=user_id,
                role=role,
                content=content,
                metadata_=metadata or {}
            )
            session.add(conv)
            await session.commit()
            await session.refresh(conv)
            return conv

    async def get_recent_conversation(
        self,
        user_id: uuid.UUID,
        limit: int = 10
    ) -> list[Conversation]:
        """Get the most recent N conversation turns for a user."""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(Conversation)
                .where(Conversation.user_id == user_id)
                .order_by(desc(Conversation.created_at))
                .limit(limit)
            )
            convs = result.scalars().all()
            return list(reversed(convs))   # Chronological order

    # ── Semantic Memory ───────────────────────────────────────────────────────

    async def save_memory(
        self,
        user_id: uuid.UUID,
        content: str,
        memory_type: str = "semantic",
        importance: float = 0.5,
    ) -> Memory:
        """Save a fact/memory about the user (without embedding for now)."""
        async with AsyncSessionLocal() as session:
            memory = Memory(
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                importance=importance,
            )
            session.add(memory)
            await session.commit()
            await session.refresh(memory)
            print(f"💾 Memory saved: {content[:50]}...")
            return memory

    async def get_all_memories(
        self,
        user_id: uuid.UUID,
        memory_type: str = None
    ) -> list[Memory]:
        """Get all memories for a user, optionally filtered by type."""
        async with AsyncSessionLocal() as session:
            query = select(Memory).where(Memory.user_id == user_id)
            if memory_type:
                query = query.where(Memory.memory_type == memory_type)
            query = query.order_by(desc(Memory.importance))
            result = await session.execute(query)
            return list(result.scalars().all())

    # ── Audit Log ─────────────────────────────────────────────────────────────

    async def log_action(
        self,
        action: str,
        user_id: uuid.UUID = None,
        agent: str = None,
        payload: dict = None,
        result: str = None,
        risk_level: str = "low"
    ):
        """Log every action RAHI takes — for safety and debugging."""
        async with AsyncSessionLocal() as session:
            log = AuditLog(
                user_id=user_id,
                agent=agent,
                action=action,
                payload=payload,
                result=result,
                risk_level=risk_level
            )
            session.add(log)
            await session.commit()

# ── Vector Search ─────────────────────────────────────────────────────────

    async def save_memory_with_embedding(
        self,
        user_id: uuid.UUID,
        content: str,
        memory_type: str = "semantic",
        importance: float = 0.5,
    ) -> Memory:
        """Save a memory AND generate+store its vector embedding."""
        from memory.embeddings import embed_text

        embedding = embed_text(content)

        async with AsyncSessionLocal() as session:
            memory = Memory(
                user_id=user_id,
                content=content,
                embedding=embedding,
                memory_type=memory_type,
                importance=importance,
            )
            session.add(memory)
            await session.commit()
            await session.refresh(memory)
            print(f"💾 Memory + embedding saved: {content[:50]}")
            return memory

    async def search_memories_semantic(
        self,
        user_id: uuid.UUID,
        query: str,
        limit: int = 5,
        threshold: float = 0.3,
    ) -> list[tuple[Memory, float]]:
        """
        Find memories semantically similar to a query.

        Returns list of (Memory, similarity_score) tuples,
        sorted by similarity (highest first).
        """
        from memory.embeddings import embed_text
        from sqlalchemy import func

        query_embedding = embed_text(query)

        async with AsyncSessionLocal() as session:
            # pgvector cosine distance operator: <=>
            # cosine_similarity = 1 - cosine_distance
            result = await session.execute(
                select(
                    Memory,
                    (1 - Memory.embedding.cosine_distance(query_embedding)).label("similarity")
                )
                .where(Memory.user_id == user_id)
                .where(Memory.embedding.is_not(None))
                .order_by(Memory.embedding.cosine_distance(query_embedding))
                .limit(limit)
            )

            rows = result.all()
            return [(row[0], float(row[1])) for row in rows if float(row[1]) >= threshold]