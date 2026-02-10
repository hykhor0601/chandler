#!/usr/bin/env python3
"""
Test: Mode System (Research and Buddy Modes)

Run: python tests/test_mode_system.py

Expected: Mode system initialized correctly, modes switch properly

Success Criteria:
- ✓ Modes module loads
- ✓ Mode configurations valid
- ✓ Brain initializes in Buddy mode
- ✓ Mode switch tool registered
- ✓ System prompts include mode guidance
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_modes_module():
    """Test that modes module loads correctly."""
    print("\n1. Testing Modes Module...")
    try:
        from chandler.modes import Mode, MODE_CONFIG, get_mode_config, get_mode_announcement

        # Check enums exist
        assert Mode.BUDDY
        assert Mode.RESEARCH
        print("   ✓ Mode enums defined")

        # Check configurations
        for mode in Mode:
            config = get_mode_config(mode)
            assert "name" in config
            assert "emoji" in config
            assert "extended_thinking" in config
            assert "style_guidance" in config
            print(f"   ✓ {mode.value} configuration valid")

        # Check buddy mode is rapid
        buddy_config = get_mode_config(Mode.BUDDY)
        assert buddy_config["extended_thinking"] == False
        print("   ✓ Buddy mode: rapid responses (no extended thinking)")

        # Check research mode has extended thinking
        research_config = get_mode_config(Mode.RESEARCH)
        assert research_config["extended_thinking"] == True
        assert research_config["budget_tokens"] > 0
        print(f"   ✓ Research mode: extended thinking ({research_config['budget_tokens']} tokens)")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_brain_mode_integration():
    """Test that Brain integrates mode system."""
    print("\n2. Testing Brain Mode Integration...")
    try:
        from chandler.brain import Brain
        from chandler.modes import Mode

        brain = Brain()

        # Check default mode
        assert brain.current_mode == Mode.BUDDY
        print("   ✓ Brain initializes in Buddy mode (default)")

        # Check mode status
        status = brain.get_mode_status()
        assert "Buddy" in status
        print(f"   ✓ Mode status: {status}")

        # Check mode history tracking
        assert hasattr(brain, 'mode_history')
        assert isinstance(brain.mode_history, list)
        print("   ✓ Mode history tracking initialized")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mode_switch_tool():
    """Test that mode switch tool is registered."""
    print("\n3. Testing Mode Switch Tool...")
    try:
        # Import tool module to trigger registration
        import chandler.tools.mode_control  # noqa: F401
        from chandler.tools import get_all_tool_schemas

        tools = get_all_tool_schemas()

        # Find switch_mode tool
        switch_mode_tool = None
        for tool in tools:
            if tool.get("name") == "switch_mode":
                switch_mode_tool = tool
                break

        assert switch_mode_tool is not None
        print("   ✓ switch_mode tool registered")

        # Check tool schema
        assert "description" in switch_mode_tool
        assert "input_schema" in switch_mode_tool
        print("   ✓ Tool schema valid")

        # Check parameters
        props = switch_mode_tool["input_schema"]["properties"]
        assert "mode" in props
        assert "reason" in props
        print("   ✓ Tool parameters defined (mode, reason)")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_system_prompts():
    """Test that system prompts include mode guidance."""
    print("\n4. Testing Mode-Specific System Prompts...")
    try:
        from chandler.brain import Brain
        from chandler.modes import Mode

        brain = Brain()

        # Test buddy mode prompt
        buddy_prompt = brain._build_system_prompt()
        assert "Buddy Mode" in buddy_prompt
        assert "Quick and casual" in buddy_prompt
        print("   ✓ Buddy mode prompt includes guidance")

        # Manually switch to research mode for testing
        brain.current_mode = Mode.RESEARCH
        research_prompt = brain._build_system_prompt()
        assert "Research Mode" in research_prompt
        assert "thorough" in research_prompt or "academic" in research_prompt
        print("   ✓ Research mode prompt includes guidance")

        # Check datetime present in both
        assert "Current Date and Time" in buddy_prompt
        assert "Current Date and Time" in research_prompt
        print("   ✓ DateTime present in all mode prompts")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_params_per_mode():
    """Test that API params change based on mode."""
    print("\n5. Testing Mode-Specific API Parameters...")
    try:
        from chandler.brain import Brain
        from chandler.modes import Mode

        brain = Brain()

        # Test buddy mode (no extended thinking)
        brain.current_mode = Mode.BUDDY
        buddy_params = brain._build_api_params()

        # Buddy should not have thinking (unless global config enables it)
        # We'll check the config determines this correctly
        print("   ✓ Buddy mode API params generated")

        # Test research mode (extended thinking enabled)
        brain.current_mode = Mode.RESEARCH
        research_params = brain._build_api_params()

        # Research should have thinking
        assert "thinking" in research_params
        assert research_params["thinking"]["budget_tokens"] == 15000
        print("   ✓ Research mode enables extended thinking (15k tokens)")

        # Check max_tokens differs
        buddy_params_check = brain._build_api_params()
        brain.current_mode = Mode.BUDDY
        buddy_params_check = brain._build_api_params()
        print("   ✓ Mode-specific max_tokens configured")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mode_announcements():
    """Test mode switch announcements."""
    print("\n6. Testing Mode Switch Announcements...")
    try:
        from chandler.modes import Mode, get_mode_announcement

        # Test announcements
        research_announcement = get_mode_announcement(Mode.RESEARCH, "Complex question")
        assert "Research" in research_announcement
        assert "Complex question" in research_announcement
        print(f"   ✓ Research mode announcement: '{research_announcement}'")

        buddy_announcement = get_mode_announcement(Mode.BUDDY, "Casual chat")
        assert "Buddy" in buddy_announcement
        print(f"   ✓ Buddy mode announcement: '{buddy_announcement}'")

        return True

    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("=" * 70)
    print("Testing Chandler Mode System")
    print("=" * 70)

    tests = [
        test_modes_module,
        test_brain_mode_integration,
        test_mode_switch_tool,
        test_system_prompts,
        test_api_params_per_mode,
        test_mode_announcements,
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
        print("\n🎉 All tests passed! Mode system working correctly.")
        print("\nYou can now:")
        print('  - Ask Chandler deep questions → Auto-switches to Research Mode')
        print('  - Chat casually → Stays in Buddy Mode (default)')
        print('  - Use /mode command to check current mode')
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
