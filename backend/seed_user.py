"""
Seed memories for the main Humayun user.
Run once: python -m backend.seed_user
"""
import asyncio
import uuid
from memory.memory_manager import MemoryManager

USER_ID = uuid.UUID("09e89f48-4142-4393-80fe-fd1f33ed4fdb")

async def seed():
    manager = MemoryManager()
    print("🌱 Seeding memories for Humayun...")

    memories = [
        ("Humayun is a CS student at SVNIT Surat, Gujarat", 0.9),
        ("Humayun is building RAHI — an AI operating system project", 0.9),
        ("Humayun's favorite programming language is Python", 0.8),
        ("Humayun prefers concise Hindi + English mixed explanations", 0.8),
        ("Humayun is doing AI research at SVNIT", 0.8),
    ]

    for content, importance in memories:
        await manager.save_memory_with_embedding(
            USER_ID, content, memory_type="semantic", importance=importance
        )

    preferences = [
        ("User prefers short bullet-point answers", 0.9),
        ("User is a Python developer — use Python examples", 0.9),
        ("Always relate answers to RAHI project when relevant", 0.8),
    ]

    for pref, importance in preferences:
        await manager.save_preference(USER_ID, pref, importance)

    print("✅ Done! Now chat will be personalized.")

asyncio.run(seed())