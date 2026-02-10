# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## ⚠️ MUST KNOW: Development vs Testing Environment

**CRITICAL**: The development environment (where Claude Code runs) is a **remote server** that does NOT have:
- Access to macOS voice input (microphone, Speech Recognition framework)
- Access to the menu bar (rumps, AppKit GUI)
- Ability to run `chandler-voice` command
- Ability to test voice-related features directly

### Testing Workflow

Since Claude Code cannot test voice features directly, follow this workflow:

1. **Write Test Scripts**: When debugging or implementing voice features, create standalone test scripts in a `tests/` or `scripts/` directory
2. **Provide Clear Instructions**: Each test script must include:
   - What it tests
   - How to run it (`python scripts/test_wake_word.py`)
   - What the expected output should be (exact text, behavior, or error messages)
   - What a successful test looks like vs. failure
3. **User Runs Tests Locally**: The user will execute the test script in their local macOS environment with voice access
4. **User Reports Results**: The user will paste the output back, allowing Claude to debug based on actual results

### Example Test Script Structure

```python
#!/usr/bin/env python3
"""
Test: Wake Word Detection Basic Functionality
Run: python scripts/test_wake_word.py
Expected: Should print "Wake word detector initialized" then listen for 10 seconds
Success: No crashes, prints detection status every second
Failure: Crashes immediately, or "Permission denied" errors
"""

import sys
sys.path.insert(0, '/Users/zhaopin/HY/chanlder')

from chandler import wake_word_asr

def test_wake_word():
    print("Initializing wake word detector...")
    detector = wake_word_asr.get_detector()
    print("✓ Wake word detector initialized")

    print("Testing permissions...")
    has_perms = wake_word_asr.request_permissions()
    print(f"{'✓' if has_perms else '✗'} Permissions: {has_perms}")

    if has_perms:
        print("Starting 10-second listening test...")
        detector.start_listening(callback=lambda: print("WAKE WORD DETECTED!"))
        import time
        time.sleep(10)
        detector.stop_listening()
        print("✓ Test complete - no crashes")
    else:
        print("✗ Cannot test listening without permissions")

if __name__ == "__main__":
    test_wake_word()
```

### When Debugging Voice Mode Crashes

1. **Create minimal reproduction script** that isolates the crashing component
2. **Add extensive logging** to identify exactly where it crashes
3. **Wrap in try/except** to catch and report errors
4. **Guide user**: "Run this script and paste the full output including any error messages"
5. **Expected output**: Document what successful execution looks like

### Do NOT:
- Try to run `chandler-voice` directly from Claude Code (will fail)
- Assume you can test voice features (you can't)
- Make changes without providing a test script for the user to verify
- Assume the fix works without user testing it locally

## Project Overview

Chandler is a personal AI assistant powered by Anthropic Claude with dual interfaces:
- **CLI Mode**: Terminal-based REPL with Rich UI (`chandler` command)
- **Voice Mode**: macOS menu bar app with "Hey Chandler" wake word activation (`chandler-voice` command)

The project features persistent memory, web search, code execution, macOS system control, vision-based GUI automation, and conversational voice interaction.

## 🚨 Known Issues & TODOs

### CRITICAL: Voice Mode Instant Crash
**Problem**: Running `chandler-voice` causes immediate process termination (`zsh: killed chandler-voice`). The terminal process is killed instantly without any error messages.

**Likely Causes**:
- macOS permissions not properly configured despite `fix_python_permissions.sh`
- Python.app Info.plist modifications not taking effect
- TCC (Transparency, Consent, and Control) database rejecting the app
- Speech Recognition framework initialization failing
- Possible code signing issues with modified Python.app

**Debug Test Available**: Run the isolation test script:
```bash
cd /Users/zhaopin/HY/chanlder
source .venv/bin/activate
python scripts/test_voice_crash.py
```

**Expected Output**:
- If all tests pass (✓), the basic components work and the crash is in menu bar app initialization
- If it crashes at a specific test, that test will identify the failing component
- The script tests in order: imports → rumps → PyObjC → Speech framework → detector init

**Manual Debug Steps**:
1. Check Console.app for crash logs: `/var/log/system.log` and crash reports
2. Verify Info.plist was actually modified: `plutil -p $(python -c "import sys; print(sys.prefix)")/Resources/Python.app/Contents/Info.plist | grep -A 1 Speech`
3. Check TCC database: `sudo sqlite3 ~/Library/Application\ Support/com.apple.TCC/TCC.db "SELECT * FROM access WHERE service='kTCCServiceSpeechRecognition'"`
4. Try launching with debugging: `lldb -- python -m chandler.menu_bar_app`
5. Check if Python.app has proper entitlements: `codesign -d --entitlements - $(python -c "import sys; print(sys.prefix)")/Resources/Python.app/Contents/MacOS/Python`

**Needs Investigation**: Whether the Speech framework initialization in `wake_word_asr.py` is causing the immediate termination.

### ✅ FIXED: Memory System Design Flaw (2026-02-10)
**Problem (RESOLVED)**: Memory system now uses automatic persistence instead of requiring LLM to manually call `remember` tool.

**Current Implementation** (✅ Working):
1. ✅ **Auto-save conversation history**: Every message automatically saved to disk (no LLM decision needed)
2. ✅ **Graceful shutdown handler**: SIGINT/SIGTERM handlers save state before exit
3. ✅ **Periodic auto-save**: Messages written to temp file immediately (crash recovery)
4. ✅ **Background fact extraction**: Every 5 messages, facts extracted automatically in background thread
5. ✅ **Crash recovery**: Temp file survives crashes in `chandler/data/temp/current_session.json`
6. ✅ **DateTime awareness**: Current date/time automatically injected into system prompt
7. ✅ **Extended thinking**: Optional deep reasoning mode for complex tasks

**Architecture Implemented**:
```python
# In Brain.chat(), after each message:
memory.auto_save_message("user", user_message)
memory.auto_save_message("assistant", response)

# On exit (signal handler in main.py and menu_bar_app.py):
brain.finalize_session()  # Commits temp file to permanent storage
memory.fact_worker.stop()

# Background thread (started in memory.py):
memory.fact_worker.schedule_extraction(recent_messages)  # Every 5 messages
```

**Files Modified**:
- ✅ `chandler/memory.py`: Added `FactExtractionWorker`, `start_session()`, `auto_save_message()`, `commit_session()`
- ✅ `chandler/brain.py`: Added auto-save calls, `finalize_session()`, datetime injection, extended thinking support
- ✅ `chandler/main.py`: Added signal handlers for graceful shutdown
- ✅ `chandler/menu_bar_app.py`: Added signal handlers and cleanup methods
- ✅ `chandler/voice_controller.py`: Added session initialization
- ✅ `chandler/config.yaml` & `chandler/config.py`: Added `extended_thinking` config section

**Backward Compatibility**: ✅ `remember` and `recall` tools still work (now supplementary)

**Documentation**: See `INTELLIGENCE_IMPROVEMENTS.md` for full details and testing instructions

**Test Suite**: Run `python tests/test_intelligence_improvements.py` to verify all features

## Setup and Development

### Installation
```bash
# Activate virtual environment
source .venv/bin/activate

# Install in development mode
pip install -e .

# For voice mode: Fix macOS permissions (required!)
./fix_python_permissions.sh
tccutil reset All org.python.python
```

### Running the Application
```bash
# CLI mode
chandler

# Voice mode (CURRENTLY BROKEN - see Known Issues)
chandler-voice
```

### Configuration
- User config: `~/.chandler/config.yaml`
- Default config: `chandler/config.yaml`
- API key can be set via `ANTHROPIC_API_KEY` environment variable or in config file
- Memory stored in: `chandler/data/memory.json`

## Architecture

### Core Components

**Brain (`chandler/brain.py`)**: Claude API client implementing the agentic tool_use loop. Manages conversation history, executes tools, handles the request/response cycle until Claude returns pure text (no tool calls), and manages intelligent mode switching between Buddy Mode (quick, casual) and Research Mode (deep, thorough with extended thinking).

**Tool System (`chandler/tools/`)**: Decorator-based tool registry (`@tool`) that auto-generates JSON schemas from Python type hints and docstrings. Tools include:
- Web: `web_search`, `web_browse`
- Execution: `run_python`, `run_shell`
- Files: `read_file`, `write_file`, `list_files`
- System: `system_control`, `computer_use`
- Memory: `remember`, `recall`
- AI News: `get_ai_news`, `search_github_ai` (fetch daily AI/ML news and trending projects)
- Modes: `switch_mode` (intelligent switching between Buddy and Research modes)

**Memory System (`chandler/memory.py`)**: Persistent storage with three-layer architecture:
1. **Short-term memory**: Auto-saved conversation sessions (`chandler/data/conversations/`)
2. **Long-term memory**: Extracted facts and user profile (`chandler/data/memory.json`)
3. **Crash recovery**: Temp file for current session (`chandler/data/temp/current_session.json`)

Features automatic persistence, background fact extraction, and graceful shutdown handlers. See `INTELLIGENCE_IMPROVEMENTS.md` for details.

**Safety Layer (`chandler/safety.py`)**: Guards against destructive operations:
- Blocks dangerous commands (`rm -rf /`, fork bombs, etc.)
- Path restrictions (only allowed directories)
- Confirmation prompts for destructive operations

### Voice Mode Architecture

Voice mode uses a dual ASR system:
1. **Wake Word Detection** (`wake_word_asr.py`): Low-power Apple Speech framework listens continuously for "chandler"
2. **High-Precision ASR** (`high_precision_asr.py`): Stub for user to implement with LLM-based transcription (Whisper, Deepgram, etc.)

**Voice Controller** (`voice_controller.py`): Orchestrates the full flow:
- Manages wake word → high-precision ASR → Brain → TTS pipeline
- Tracks input mode (voice vs text) to route responses correctly
- Thread-safe state management

**Menu Bar App** (`menu_bar_app.py`): Built with rumps (macOS menu bar framework):
- Displays emoji state indicators (💬🎤🤔🗣️⚠️)
- Shows conversation history with scrollable view
- Text input field for typing messages
- Manual controls (stop listening, clear, quit)

**Response Routing**: Voice input → TTS output, Text input → silent output (displayed in menu only)

### UI Adapters

The Brain accepts different UI adapters:
- **CLI Mode**: Uses Rich library (`chandler/ui.py`) for colored console output with spinners
- **Voice Mode**: Uses `VoiceUIAdapter` (`chandler/voice_ui.py`) that updates menu bar state instead of console

This adapter pattern allows the same Brain implementation to work seamlessly in both modes.

## Key Design Patterns

### Tool Registration
Tools use a decorator pattern with automatic schema generation:
```python
@tool(name="web_search", description="Search the web")
def web_search(query: str) -> str:
    """
    Args:
        query: The search query string
    """
    # Implementation
```

Type hints → JSON schema types, docstrings → parameter descriptions.

### Agentic Loop
Brain implements a loop that:
1. Sends user message + tool schemas to Claude
2. Parses response for text and tool_use blocks
3. Executes tools via `execute_tool()`
4. Appends tool results to conversation
5. Loops until Claude responds with only text (stop condition)

### Voice State Machine
Voice controller manages states: `idle` → `listening` → `thinking` → `speaking` → `idle`

Wake word detection runs continuously on background thread. When triggered, starts high-precision ASR on separate thread (allows cancellation). Input mode is tracked to determine response routing.

## Important Implementation Details

### macOS Permissions
Voice mode requires Speech Recognition and Microphone permissions. Python.app's Info.plist must declare these usage purposes. The `fix_python_permissions.sh` script adds required keys:
- `NSSpeechRecognitionUsageDescription`
- `NSMicrophoneUsageDescription`

After modifying Info.plist, TCC cache must be reset with `tccutil reset All org.python.python`.

**WARNING**: Currently the voice mode crashes immediately even after following these steps. See Known Issues section.

### API Timeout
All Claude API calls have a 5-minute timeout (configurable via `api_timeout` in config). This prevents hanging on long-running operations.

### Computer Control Tool
The `computer_use` tool (`chandler/tools/computer_use.py`) implements vision-based GUI automation:
- Takes screenshot
- Sends to vision model (GPT-4o) with action request
- Executes mouse/keyboard actions via pyautogui
- Iterates until task complete or max iterations reached

Requires separate vision model configured in config (OpenAI-compatible endpoint).

### Safety Checks
Before executing shell commands, `safety.py` checks:
1. Is command completely blocked? (dangerous patterns)
2. Does command require confirmation? (destructive but allowed)
3. Are file paths within allowed directories?

User must confirm destructive operations unless `require_confirmation_for_destructive: false` in config.

## Common Tasks

### Adding a New Tool
1. Create function in `chandler/tools/` directory
2. Add `@tool(name="...", description="...")` decorator
3. Use type hints for parameters
4. Add docstring with parameter descriptions
5. Tool is automatically registered and available to Claude

### Modifying System Prompt
Edit `SYSTEM_PROMPT` in `chandler/brain.py`. Memory context is automatically injected via `{memory_context}` placeholder.

### Customizing Wake Word
Change `voice_mode.wake_word` in config file. The wake word detector matches any phrase containing the word (case-insensitive).

### Implementing High-Precision ASR
Replace the stub in `chandler/high_precision_asr.py`:
- Implement `transcribe_audio()` function
- Must respect `cancel_event` for user cancellation
- Record audio, transcribe, return text string
- See VOICE_MODE.md for examples

## Testing and Debugging

### Logs
Voice mode logs to `/tmp/chandler_voice.log` with detailed state transitions.

### CLI Mode Testing
Run `chandler` to test in terminal. Use `/help` to see commands, `/memory` to view stored facts, `/clear` to reset conversation.

### Voice Mode Testing (Currently Broken)
Launch `chandler-voice` and check menu bar icon appears. **NOTE: Currently crashes immediately - see Known Issues.**

### Debugging Voice Mode Crash
```bash
# Check crash logs
open /Library/Logs/DiagnosticReports/
tail -f /var/log/system.log

# Verify Python.app Info.plist modifications
plutil -p $(python -c "import sys; print(sys.prefix)")/Resources/Python.app/Contents/Info.plist | grep -A 1 Speech

# Run with debugger
lldb -- python -m chandler.menu_bar_app
```

### Memory Inspection
Memory stored in multiple locations:
- **Long-term facts**: `chandler/data/memory.json` (can be viewed with `/memory` CLI command)
- **Session history**: `chandler/data/conversations/session_*.json` (per-session conversation logs)
- **Crash recovery**: `chandler/data/temp/current_session.json` (current session, deleted on graceful exit)

**NEW (2026-02-10)**: Memory is now automatically saved on every message. No data loss on Ctrl+C or crashes! See `INTELLIGENCE_IMPROVEMENTS.md` for details.

## Dependencies

Key dependencies:
- `anthropic`: Claude API client
- `rich`: CLI UI (colors, spinners, formatting)
- `rumps`: macOS menu bar app framework
- `pyobjc-framework-*`: macOS native APIs (Speech, Cocoa, Quartz)
- `duckduckgo-search`: Web search implementation
- `pyautogui`, `pillow`, `opencv-python`: Computer control/screenshots

All dependencies in `requirements.txt`. Install with `pip install -e .` from project root.

## File Organization

- `chandler/main.py`: CLI entry point
- `chandler/menu_bar_app.py`: Voice mode entry point (CURRENTLY CRASHES)
- `chandler/brain.py`: Core Claude API client
- `chandler/tools/`: All tool implementations
- `chandler/config.py`: Config loader (merges default + user config)
- `chandler/memory.py`: Persistent memory system with automatic session saving and background fact extraction
- `chandler/safety.py`: Command safety checks
- `chandler/voice_*.py`: Voice mode components (controller, UI adapter, ASR)
- `chandler/computer_control.py`: Vision-based automation
- `chandler/ui.py`: CLI UI with Rich

## Configuration Priority

Config values are resolved in this order (highest priority first):
1. Environment variables (e.g., `ANTHROPIC_API_KEY`)
2. User config (`~/.chandler/config.yaml`)
3. Default config (`chandler/config.yaml`)

When modifying config behavior, update `chandler/config.py` which handles merging.
