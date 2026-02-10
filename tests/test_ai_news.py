#!/usr/bin/env python3
"""
Test: AI News Tool

Run: python tests/test_ai_news.py

Expected: Fetches AI news from GitHub, Hacker News, and Papers with Code

Success: Displays formatted news report with trending projects and articles
Failure: Network errors or empty results
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_get_ai_news():
    """Test fetching AI news from all sources."""
    print("\n" + "=" * 70)
    print("Testing AI News Tool - All Sources")
    print("=" * 70 + "\n")

    try:
        from chandler.tools.ai_news import get_ai_news

        print("Fetching AI news from all sources...")
        print("(This may take 10-20 seconds...)\n")

        result = get_ai_news()

        print(result)
        print("\n" + "=" * 70)
        print("✓ AI news fetched successfully!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_github_search():
    """Test GitHub search for AI/ML repos."""
    print("\n" + "=" * 70)
    print("Testing GitHub Search - Query: 'llm agent'")
    print("=" * 70 + "\n")

    try:
        from chandler.tools.ai_news import search_github_ai

        print("Searching GitHub for 'llm agent'...\n")

        result = search_github_ai("llm agent")

        print(result)
        print("\n" + "=" * 70)
        print("✓ GitHub search completed successfully!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_github_trending():
    """Test fetching GitHub trending AI repos."""
    print("\n" + "=" * 70)
    print("Testing GitHub Trending - AI/ML Only")
    print("=" * 70 + "\n")

    try:
        from chandler.tools.ai_news import get_ai_news

        print("Fetching trending AI/ML repos from GitHub...\n")

        result = get_ai_news(sources="github")

        print(result)
        print("\n" + "=" * 70)
        print("✓ GitHub trending fetched successfully!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_hackernews():
    """Test fetching Hacker News AI stories."""
    print("\n" + "=" * 70)
    print("Testing Hacker News - AI Stories")
    print("=" * 70 + "\n")

    try:
        from chandler.tools.ai_news import get_ai_news

        print("Fetching AI stories from Hacker News...\n")

        result = get_ai_news(sources="hackernews")

        print(result)
        print("\n" + "=" * 70)
        print("✓ Hacker News fetched successfully!")
        print("=" * 70)
        return True

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("AI News Tool Test Suite")
    print("=" * 70)
    print("\nNote: These tests require internet connection and may take 30-60 seconds")
    print("Some sources may fail due to rate limiting or changes in website structure\n")

    tests = [
        ("GitHub Trending", test_github_trending),
        ("Hacker News", test_hackernews),
        ("GitHub Search", test_github_search),
        ("All Sources", test_get_ai_news),
    ]

    results = []
    for name, test_func in tests:
        try:
            print(f"\n{'=' * 70}")
            print(f"Running: {name}")
            print('=' * 70)
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Test '{name}' failed with exception: {e}")
            results.append((name, False))

    # Summary
    print("\n\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status} - {name}")

    print("\n" + "=" * 70)
    print(f"Result: {passed}/{total} tests passed")
    print("=" * 70)

    if passed == total:
        print("\n🎉 All tests passed! AI news tool is working correctly.")
        print("\nYou can now ask Chandler:")
        print('  - "What\'s the latest AI news?"')
        print('  - "Show me trending AI projects on GitHub"')
        print('  - "Search GitHub for LLM agents"')
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("Some failures are expected if:")
        print("  - Website structure changed")
        print("  - Rate limiting occurred")
        print("  - Network issues")
        print("\nTry running again or check individual sources.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
