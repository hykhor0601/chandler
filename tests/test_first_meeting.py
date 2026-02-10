#!/usr/bin/env python3
"""
Test: First Meeting Protocol

Run: python tests/test_first_meeting.py

Expected: Brain detects new user and includes first meeting guidance

Success Criteria:
- ✓ Memory detects new user correctly
- ✓ System prompt includes first meeting guidance
- ✓ Guidance removed when user has memories
"""

import sys
import os
import tempfile
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_new_user_detection():
    """Test that memory correctly detects new users."""
    print("\n1. Testing New User Detection...")
    try:
        # Create a temporary memory file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            empty_memory = {"user_profile": {}, "facts": {}, "conversation_summaries": []}
            json.dump(empty_memory, f)
            temp_path = f.name

        # Monkey-patch the memory path
        from chandler.memory import Memory
        from chandler.config import config

        # Save original path
        original_path = config.data_dir / "memory.json"

        # Create memory with empty data
        memory = Memory()
        memory._path = Path(temp_path)
        memory._data = {"user_profile": {}, "facts": {}, "conversation_summaries": []}

        # Test new user detection
        assert memory.is_new_user() == True
        print("   ✓ Detects new user (empty memory)")

        # Add some data
        memory._data["user_profile"]["name"] = "Alice"

        # Should no longer be new user
        assert memory.is_new_user() == False
        print("   ✓ Detects existing user (has profile data)")

        # Cleanup
        os.unlink(temp_path)

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_first_meeting_prompt():
    """Test that system prompt includes first meeting guidance for new users."""
    print("\n2. Testing First Meeting Prompt Injection...")
    try:
        from chandler.brain import Brain
        from chandler.memory import Memory
        import tempfile
        import json

        # Create a temporary memory file with empty data
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            empty_memory = {"user_profile": {}, "facts": {}, "conversation_summaries": []}
            json.dump(empty_memory, f)
            temp_path = f.name

        # Monkey-patch memory to use temp file
        from chandler import memory as memory_module
        original_path = memory_module.memory._path
        memory_module.memory._path = Path(temp_path)
        memory_module.memory._data = {"user_profile": {}, "facts": {}, "conversation_summaries": []}

        # Create brain
        brain = Brain()

        # Build system prompt
        prompt = brain._build_system_prompt()

        # Check for first meeting guidance
        assert "First Meeting Protocol" in prompt
        print("   ✓ First meeting guidance included in prompt")

        assert "Ask for their name" in prompt
        print("   ✓ Prompt encourages asking for name")

        assert "Show genuine interest" in prompt
        print("   ✓ Prompt encourages showing curiosity")

        # Now test with existing user
        memory_module.memory._data["user_profile"]["name"] = "Bob"

        # Rebuild prompt
        prompt = brain._build_system_prompt()

        # First meeting guidance should NOT be present
        assert "First Meeting Protocol" not in prompt
        print("   ✓ First meeting guidance removed for existing user")

        # Cleanup
        memory_module.memory._path = original_path
        os.unlink(temp_path)

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_general_curiosity_guidance():
    """Test that system prompt encourages curiosity in general."""
    print("\n3. Testing General Curiosity Guidance...")
    try:
        from chandler.brain import Brain

        brain = Brain()
        prompt = brain._build_system_prompt()

        # Check for general curiosity guidance (in base prompt)
        assert "Show genuine curiosity" in prompt or "curious" in prompt.lower()
        print("   ✓ System prompt encourages curiosity")

        assert "name" in prompt.lower()
        print("   ✓ System prompt mentions asking for name")

        assert "follow-up" in prompt.lower() or "follow up" in prompt.lower()
        print("   ✓ System prompt encourages follow-up questions")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing First Meeting Protocol")
    print("=" * 70)

    tests = [
        test_new_user_detection,
        test_first_meeting_prompt,
        test_general_curiosity_guidance,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n   ✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)

    print("\n" + "=" * 70)
    print("Test Results")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results), 1):
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {test.__doc__.strip()}")

    print("\n" + "=" * 70)
    print(f"Summary: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n🎉 All tests passed! First meeting protocol working.")
        print("\nChandler will now:")
        print("  ✓ Introduce itself on first meeting")
        print("  ✓ Ask for your name naturally")
        print("  ✓ Show genuine interest in you")
        print("  ✓ Remember what you share")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
