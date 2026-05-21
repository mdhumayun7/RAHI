"""
RAHI Vector Search — Test Suite
=================================
Tests semantic memory storage and retrieval.
"""

import asyncio
from memory.memory_manager import MemoryManager


async def run_vector_tests():
    manager = MemoryManager()

    print("\n" + "="*60)
    print("🧪 RAHI VECTOR SEARCH TESTS")
    print("="*60)

    # ── Setup: Create test user ───────────────────────────────────
    print("\n--- Setup: Creating test user ---")
    user = await manager.create_user(
        name="Humayun_VectorTest",
        email=f"vector_test_{__import__('time').time():.0f}@test.com"
    )
    print(f"✅ Test user: {user.id}")

    # ── Test 1: Save memories WITH embeddings ─────────────────────
    print("\n--- Test 1: Saving memories with embeddings ---")

    facts = [
        ("Humayun is a student at SVNIT Surat studying Computer Science", 0.9),
        ("Humayun is building RAHI, an AI operating system project",       0.9),
        ("Humayun's favorite programming language is Python",              0.7),
        ("RAHI uses ReAct reasoning loop for decision making",             0.8),
        ("Surat is a city in Gujarat, India known for diamonds and textiles", 0.5),
        ("The weather in Surat is typically hot and humid",                0.4),
    ]

    for content, importance in facts:
        await manager.save_memory_with_embedding(
            user.id, content, importance=importance
        )

    print(f"✅ {len(facts)} memories saved with embeddings")

    # ── Test 2: Semantic Search ───────────────────────────────────
    print("\n--- Test 2: Semantic Search ---")

    queries = [
        "Where does Humayun study?",
        "What is Humayun working on?",
        "What coding language does he prefer?",
        "Tell me about the RAHI project",
        "What is the climate like?",
    ]

    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        results = await manager.search_memories_semantic(
            user.id, query, limit=2
        )
        if results:
            for memory, score in results:
                print(f"   [{score:.3f}] {memory.content[:70]}")
        else:
            print("   No results found")

    print("\n" + "="*60)
    print("✅ VECTOR SEARCH TESTS COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(run_vector_tests())