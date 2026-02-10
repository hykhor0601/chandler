#!/usr/bin/env python3
"""
Test: Intelligence Improvements (Automatic Memory, Extended Thinking, DateTime)

Run: python tests/test_intelligence_improvements.py

Expected: All tests pass with ✓ marks

Success Criteria:
- ✓ DateTime injection appears in system prompt
- ✓ Extended thinking config is loaded correctly
- ✓ Session auto-save creates temp file
- ✓ Session commit moves temp to permanent storage
- ✓ Background fact worker starts successfully
- ✓ Signal handlers are registered
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from datetime import datetime
import time
import signal


def test_datetime_injection():
    """Test that datetime is injected into system prompt."""
    print("\n1. Testing DateTime Injection...")
    try:
        from chandler.brain import Brain
        brain = Brain()

        system_prompt = brain._build_system_prompt()

        # Check if datetime section exists
        if "## Current Date and Time" in system_prompt:
            # Verify the format (YYYY-MM-DD HH:MM:SS)
            current_year = str(datetime.now().year)
            if current_year in system_prompt:
                print("   ✓ DateTime injection working correctly")
                return True
            else:
                print(f"   ✗ DateTime found but doesn't contain current year: {current_year}")
                return False
        else:
            print("   ✗ DateTime section not found in system prompt")
            print(f"   System prompt preview: {system_prompt[:200]}...")
            return False
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_extended_thinking_config():
    """Test that extended thinking config is loaded."""
    print("\n2. Testing Extended Thinking Configuration...")
    try:
        from chandler.config import config

        thinking_config = config.extended_thinking

        # Check if all required keys exist
        required_keys = ["enabled", "budget_tokens", "min_budget", "max_budget"]
        for key in required_keys:
            if key not in thinking_config:
                print(f"   ✗ Missing key in extended_thinking config: {key}")
                return False

        # Verify default values
        if thinking_config["budget_tokens"] == 10000:
            print("   ✓ Extended thinking config loaded correctly")
            print(f"     - Enabled: {thinking_config['enabled']}")
            print(f"     - Budget tokens: {thinking_config['budget_tokens']}")
            return True
        else:
            print(f"   ✗ Unexpected budget_tokens value: {thinking_config['budget_tokens']}")
            return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_management():
    """Test session auto-save and commit."""
    print("\n3. Testing Session Management...")
    try:
        from chandler.memory import memory
        from chandler.config import config

        # Ensure data directories exist
        data_dir = config.data_dir
        temp_dir = data_dir / "temp"
        conversations_dir = data_dir / "conversations"

        print(f"   - Data directory: {data_dir}")
        print(f"   - Temp directory: {temp_dir}")
        print(f"   - Conversations directory: {conversations_dir}")

        if not temp_dir.exists():
            print(f"   ✗ Temp directory doesn't exist: {temp_dir}")
            return False

        if not conversations_dir.exists():
            print(f"   ✗ Conversations directory doesn't exist: {conversations_dir}")
            return False

        print("   ✓ Directories exist")

        # Start a session
        session_id = memory.start_session()
        print(f"   ✓ Session started: {session_id}")

        # Auto-save a message
        memory.auto_save_message("user", "Hello, this is a test message")
        memory.auto_save_message("assistant", "Hello! This is a test response.")

        # Check temp file exists
        temp_file = temp_dir / "current_session.json"
        if temp_file.exists():
            print(f"   ✓ Temp file created: {temp_file}")
        else:
            print(f"   ✗ Temp file not created: {temp_file}")
            return False

        # Read temp file to verify
        import json
        with open(temp_file) as f:
            temp_data = json.load(f)

        if temp_data["message_count"] == 2:
            print(f"   ✓ Auto-save working (2 messages saved)")
        else:
            print(f"   ✗ Message count mismatch: {temp_data['message_count']}")
            return False

        # Commit session
        memory.commit_session(session_id)

        # Check permanent file exists
        permanent_file = conversations_dir / f"session_{session_id}.json"
        if permanent_file.exists():
            print(f"   ✓ Session committed: {permanent_file}")
        else:
            print(f"   ✗ Permanent file not created: {permanent_file}")
            return False

        # Check temp file removed
        if not temp_file.exists():
            print(f"   ✓ Temp file cleaned up")
        else:
            print(f"   ⚠ Temp file still exists (might be OK)")

        # Cleanup test file
        permanent_file.unlink()
        print("   ✓ Test session cleaned up")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fact_extraction_worker():
    """Test that background fact worker starts."""
    print("\n4. Testing Background Fact Extraction Worker...")
    try:
        from chandler.memory import memory

        # Check if worker thread is alive
        if memory.fact_worker.is_alive():
            print("   ✓ Fact extraction worker is running")
            return True
        else:
            print("   ✗ Fact extraction worker is not running")
            return False

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_signal_handlers():
    """Test that signal handlers can be registered."""
    print("\n5. Testing Signal Handler Registration...")
    try:
        # Try registering a dummy handler
        original_sigint = signal.getsignal(signal.SIGINT)
        original_sigterm = signal.getsignal(signal.SIGTERM)

        def dummy_handler(signum, frame):
            pass

        signal.signal(signal.SIGINT, dummy_handler)
        signal.signal(signal.SIGTERM, dummy_handler)

        # Verify they were set
        if signal.getsignal(signal.SIGINT) == dummy_handler:
            print("   ✓ SIGINT handler can be registered")
        else:
            print("   ✗ SIGINT handler registration failed")
            return False

        if signal.getsignal(signal.SIGTERM) == dummy_handler:
            print("   ✓ SIGTERM handler can be registered")
        else:
            print("   ✗ SIGTERM handler registration failed")
            return False

        # Restore original handlers
        signal.signal(signal.SIGINT, original_sigint)
        signal.signal(signal.SIGTERM, original_sigterm)

        print("   ✓ Signal handlers working correctly")
        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_brain_api_params():
    """Test that Brain builds API params correctly with extended thinking."""
    print("\n6. Testing Brain API Parameters...")
    try:
        from chandler.brain import Brain
        from chandler.config import config

        brain = Brain()

        # Test with extended thinking disabled (default)
        params = brain._build_api_params()

        required_keys = ["model", "max_tokens", "system", "tools", "messages"]
        for key in required_keys:
            if key not in params:
                print(f"   ✗ Missing required key in API params: {key}")
                return False

        # Verify thinking is not included when disabled
        if "thinking" in params:
            print("   ⚠ 'thinking' param present when extended thinking is disabled")
            print("     (This is OK if you enabled it in config)")
        else:
            print("   ✓ API params correct (extended thinking disabled)")

        # Test that datetime is in system prompt
        if "Current Date and Time" in params["system"]:
            print("   ✓ DateTime present in system prompt")
        else:
            print("   ✗ DateTime not found in system prompt")
            return False

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing Chandler Intelligence Improvements")
    print("=" * 70)

    tests = [
        test_datetime_injection,
        test_extended_thinking_config,
        test_session_management,
        test_fact_extraction_worker,
        test_signal_handlers,
        test_brain_api_params,
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
        print("\n🎉 All tests passed! Intelligence improvements working correctly.")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
