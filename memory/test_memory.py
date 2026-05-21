"""
RAHI Memory System — Test Suite
=================================
Tests: user creation, conversation storage, memory retrieval
"""

import asyncio
from memory.database import test_connection
from memory.memory_manager import MemoryManager


async def run_tests():
    manager = MemoryManager()

    print("\n" + "="*60)
    print("🧪 RAHI MEMORY SYSTEM TESTS")
    print("="*60)

    # ── Test 1: DB Connection ─────────────────────────────────────
    print("\n--- Test 1: Database Connection ---")
    await test_connection()

    # ── Test 2: Create User ───────────────────────────────────────
    print("\n--- Test 2: Create User ---")
    user = await manager.create_user(
        name="Humayun",
        email="humayun@svnit.ac.in"
    )
    print(f"✅ User ID: {user.id}")
    print(f"✅ User Name: {user.name}")

    # ── Test 3: Save Conversation ─────────────────────────────────
    print("\n--- Test 3: Save Conversation ---")
    await manager.save_conversation(user.id, "user",      "Mera naam Humayun hai, main SVNIT mein padhta hoon")
    await manager.save_conversation(user.id, "assistant", "Namaste Humayun! Main RAHI hoon, aapki kaise madad kar sakta hoon?")
    await manager.save_conversation(user.id, "user",      "Main AI research kar raha hoon")
    print("✅ 3 conversation turns saved")

    # ── Test 4: Retrieve Conversation ────────────────────────────
    print("\n--- Test 4: Retrieve Conversation ---")
    history = await manager.get_recent_conversation(user.id, limit=10)
    for turn in history:
        print(f"  [{turn.role.upper()}]: {turn.content[:60]}")

    # ── Test 5: Save Memories ─────────────────────────────────────
    print("\n--- Test 5: Save Memories ---")
    await manager.save_memory(user.id, "User's name is Humayun",                         importance=0.9)
    await manager.save_memory(user.id, "Humayun studies at SVNIT Surat, Gujarat",        importance=0.8)
    await manager.save_memory(user.id, "Humayun is working on RAHI — an AI project",     importance=0.9)
    await manager.save_memory(user.id, "Humayun prefers concise technical explanations", importance=0.7)

    # ── Test 6: Retrieve Memories ─────────────────────────────────
    print("\n--- Test 6: Retrieve Memories ---")
    memories = await manager.get_all_memories(user.id)
    for m in memories:
        print(f"  [importance: {m.importance}] {m.content}")

    # ── Test 7: Audit Log ─────────────────────────────────────────
    print("\n--- Test 7: Audit Log ---")
    await manager.log_action(
        action="test_memory_system",
        user_id=user.id,
        agent="memory_manager",
        payload={"test": "phase_2"},
        result="success",
        risk_level="low"
    )
    print("✅ Action logged to audit trail")

    print("\n" + "="*60)
    print("✅ ALL MEMORY TESTS COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(run_tests())