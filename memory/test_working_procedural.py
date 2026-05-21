"""
RAHI Working + Procedural Memory — Test Suite
"""

import asyncio
import uuid
from memory.working_memory import WorkingMemory
from memory.memory_manager import MemoryManager


def test_working_memory():
    wm = WorkingMemory()

    print("\n" + "="*60)
    print("🧪 WORKING MEMORY TESTS (Redis)")
    print("="*60)

    # Test 1: Redis connection
    print("\n--- Test 1: Redis Connection ---")
    assert wm.ping(), "Redis not reachable!"
    print("✅ Redis connected!")

    # Test 2: Session messages
    print("\n--- Test 2: Session Messages ---")
    session_id = str(uuid.uuid4())

    wm.add_message(session_id, "user",      "Mera naam Humayun hai")
    wm.add_message(session_id, "assistant", "Namaste Humayun!")
    wm.add_message(session_id, "user",      "Main RAHI bana raha hoon")
    wm.add_message(session_id, "assistant", "RAHI ek amazing project hai!")

    messages = wm.get_messages(session_id)
    print(f"✅ {len(messages)} messages stored in Redis")
    for m in messages:
        print(f"  [{m['role'].upper()}]: {m['content']}")

    # Test 3: Context string
    print("\n--- Test 3: Context String for LLM ---")
    context = wm.get_context_string(session_id)
    print("✅ Context string:")
    print(context)

    # Test 4: Task state
    print("\n--- Test 4: Task State ---")
    wm.set_task_state(session_id, {
        "goal":         "Calculate 15% of 840",
        "current_step": 2,
        "observations": ["calculator returned 126.0"],
    })
    state = wm.get_task_state(session_id)
    print(f"✅ Task state saved: goal='{state['goal']}'")
    print(f"   Step: {state['current_step']}, Observations: {state['observations']}")

    # Test 5: User session
    print("\n--- Test 5: User Session ---")
    user_id = str(uuid.uuid4())
    wm.set_user_session(session_id, user_id, "Humayun")
    user_info = wm.get_user_session(session_id)
    print(f"✅ User session: name={user_info['name']}")

    # Test 6: Message count
    print("\n--- Test 6: Message Count ---")
    count = wm.get_message_count(session_id)
    print(f"✅ Total messages in session: {count}")

    # Test 7: Clear session
    print("\n--- Test 7: Clear Session ---")
    wm.clear_session(session_id)
    assert wm.get_message_count(session_id) == 0
    print("✅ Session cleared!")

    print("\n✅ ALL WORKING MEMORY TESTS PASSED!")


async def test_procedural_memory():
    manager = MemoryManager()

    print("\n" + "="*60)
    print("🧪 PROCEDURAL MEMORY TESTS")
    print("="*60)

    # Setup user
    import time
    user = await manager.create_user(
        name="Humayun_Procedural",
        email=f"proc_{time.time():.0f}@test.com"
    )

    # Test 1: Save preferences
    print("\n--- Test 1: Save Preferences ---")
    prefs = [
        ("User prefers concise bullet-point answers",              0.8),
        ("User is a Python developer, avoid JavaScript examples",  0.9),
        ("User is building RAHI — always relate answers to RAHI",  0.9),
        ("User is a CS student at SVNIT Surat",                    0.7),
        ("User prefers Hindi + English mixed explanations",         0.8),
    ]

    for pref, importance in prefs:
        await manager.save_preference(user.id, pref, importance)

    print(f"✅ {len(prefs)} preferences saved")

    # Test 2: Retrieve preferences
    print("\n--- Test 2: Retrieve Preferences ---")
    all_prefs = await manager.get_preferences(user.id)
    for p in all_prefs:
        print(f"  [procedural | {p.importance}] {p.content}")

    # Test 3: As string (for LLM prompt injection)
    print("\n--- Test 3: Preferences as LLM Prompt String ---")
    pref_string = await manager.get_preferences_as_string(user.id)
    print("✅ This gets injected into RAHI's system prompt:")
    print(pref_string)

    print("\n✅ ALL PROCEDURAL MEMORY TESTS PASSED!")


if __name__ == "__main__":
    # Working memory is sync (Redis)
    test_working_memory()

    # Procedural memory is async (PostgreSQL)
    asyncio.run(test_procedural_memory())