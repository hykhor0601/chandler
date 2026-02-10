#!/usr/bin/env python3
"""
Test: Voice Mode Crash Debugging
Purpose: Isolate which component causes the instant crash when running chandler-voice
Run: cd /Users/zhaopin/HY/chanlder && source .venv/bin/activate && python scripts/test_voice_crash.py

Expected Outputs:
- Success: All tests pass, prints "✓" for each component
- Failure: Crashes at a specific step, showing which component is the culprit

Test Progression:
1. Import basic Python modules
2. Import rumps (menu bar framework)
3. Import PyObjC frameworks (AppKit, Foundation)
4. Import Speech framework (likely culprit)
5. Initialize rumps app
6. Initialize wake word detector
7. Create full menu bar app

The test will stop at the first failing component and report it.
"""

import sys
import traceback

print("=" * 60)
print("VOICE MODE CRASH DEBUG TEST")
print("=" * 60)

# Test 1: Basic imports
print("\n[1/7] Testing basic imports...")
try:
    import logging
    from typing import List, Tuple
    print("✓ Basic imports successful")
except Exception as e:
    print(f"✗ FAILED at basic imports: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 2: rumps import
print("\n[2/7] Testing rumps import...")
try:
    import rumps
    print(f"✓ rumps imported successfully (version: {rumps.__version__ if hasattr(rumps, '__version__') else 'unknown'})")
except ImportError as e:
    print(f"✗ FAILED: rumps not installed")
    print(f"   Install with: pip install rumps")
    sys.exit(1)
except Exception as e:
    print(f"✗ FAILED at rumps import: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 3: PyObjC basic imports
print("\n[3/7] Testing PyObjC imports...")
try:
    from Foundation import NSMakeRect, NSObject
    from AppKit import (
        NSScrollView, NSTextView, NSTextField, NSButton, NSView,
        NSMakePoint, NSMakeSize, NSTextAlignment,
        NSColor, NSFont, NSAttributedString,
        NSBezelBorder, NSMenu, NSMenuItem,
    )
    print("✓ PyObjC basic imports successful")
except ImportError as e:
    print(f"✗ FAILED: PyObjC not installed properly")
    print(f"   Should be included in Python 3.13 on macOS")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"✗ FAILED at PyObjC imports: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Speech framework import (LIKELY CULPRIT)
print("\n[4/7] Testing Speech framework import...")
try:
    from Speech import SFSpeechRecognizer
    print("✓ Speech framework imported successfully")
    print("   NOTE: If the process gets killed AFTER this line,")
    print("        the issue is with Speech framework initialization,")
    print("        not the import itself.")
except ImportError as e:
    print(f"✗ FAILED: Speech framework not available")
    print(f"   This is expected if pyobjc-framework-Speech is not installed")
    print(f"   Install with: pip install pyobjc-framework-Speech")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"✗ FAILED at Speech framework import: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Create minimal rumps app
print("\n[5/7] Testing minimal rumps app creation...")
try:
    class MinimalApp(rumps.App):
        def __init__(self):
            super().__init__(name="Test", title="🧪", icon=None)

    test_app = MinimalApp()
    print("✓ Minimal rumps app created successfully")
    print("   (Not running it, just testing initialization)")
except Exception as e:
    print(f"✗ FAILED at rumps app creation: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 6: Import wake_word_asr
print("\n[6/7] Testing wake_word_asr import...")
try:
    sys.path.insert(0, '/Users/zhaopin/HY/chanlder')
    from chandler import wake_word_asr
    print("✓ wake_word_asr imported successfully")
except Exception as e:
    print(f"✗ FAILED at wake_word_asr import: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 7: Initialize wake word detector (VERY LIKELY CRASH POINT)
print("\n[7/7] Testing wake word detector initialization...")
print("   WARNING: If process gets killed here, the issue is in")
print("            wake_word_asr.get_detector() initialization")
try:
    detector = wake_word_asr.get_detector()
    print("✓ Wake word detector initialized successfully")
    print("   This is surprising! The detector initialized without crashing.")
except Exception as e:
    print(f"✗ FAILED at detector initialization: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 8: Check permissions
print("\n[8/8] Testing permission request...")
try:
    has_perms = wake_word_asr.request_permissions()
    print(f"{'✓' if has_perms else '⚠'} Permissions granted: {has_perms}")
    if not has_perms:
        print("   This is expected if you haven't granted permissions yet")
        print("   Go to System Settings > Privacy & Security > Microphone")
        print("   and System Settings > Privacy & Security > Speech Recognition")
except Exception as e:
    print(f"✗ FAILED at permission check: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("🎉 ALL TESTS PASSED!")
print("=" * 60)
print("\nConclusion:")
print("If you see this message, the voice mode crash is NOT caused by:")
print("  - Basic imports")
print("  - rumps framework")
print("  - PyObjC frameworks")
print("  - Speech framework import")
print("  - Wake word detector initialization")
print("\nThe crash must be happening elsewhere, possibly:")
print("  - VoiceController initialization")
print("  - Full menu bar app creation")
print("  - Something in menu_bar_app.py's __init__")
print("\nNext step: Run 'chandler-voice' and see if it still crashes.")
print("If it does, the issue is in ChandlerMenuBarApp.__init__() or app.run()")
