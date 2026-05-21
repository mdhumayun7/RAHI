"""
RAHI ReAct Engine — Test Suite
================================
3 tests of increasing complexity to verify the reasoning loop works.
"""

from brain.react_engine import ReActEngine


def test_1_simple_math():
    """Test: Can RAHI do a multi-step math calculation?"""
    print("\n" + "🧪 TEST 1: Simple Math".center(60, "="))
    engine = ReActEngine(max_steps=4, verbose=True)
    result = engine.run("What is 15% of 840?")
    print(f"\n📌 Returned: {result}")


def test_2_factual_search():
    """Test: Can RAHI search for information and answer?"""
    print("\n" + "🧪 TEST 2: Factual Search".center(60, "="))
    engine = ReActEngine(max_steps=4, verbose=True)
    result = engine.run("Where is SVNIT located?")
    print(f"\n📌 Returned: {result}")


def test_3_multi_step():
    """Test: Can RAHI use multiple tools in sequence?"""
    print("\n" + "🧪 TEST 3: Multi-Step Reasoning".center(60, "="))
    engine = ReActEngine(max_steps=6, verbose=True)
    result = engine.run(
        "What is the weather in Surat today, and what is 20% of 500?"
    )
    print(f"\n📌 Returned: {result}")


if __name__ == "__main__":
    test_1_simple_math()
    test_2_factual_search()
    test_3_multi_step()

    print("\n" + "="*60)
    print("✅ All ReAct tests complete!")
    print("="*60)