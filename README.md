# 💬 Chandler — AI Voice & Text Assistant

A personal AI assistant powered by Anthropic Claude with **dual interfaces**:
- 🎤 **Voice Mode**: "Hey Chandler" wake word activation (like Siri)
- ⌨️ **CLI Mode**: Terminal-based text interface

**Features**: Persistent memory, web search, code execution, macOS system control, vision-based GUI automation, and voice interaction.

---

## 🚀 Quick Start

### Prerequisites

- **macOS** (required for voice mode and system control)
- **Python 3.10+**
- **Anthropic API key** ([Get one here](https://console.anthropic.com/))

### Installation

```bash
# 1. Navigate to project
cd /path/to/chandler

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate it
source .venv/bin/activate

# 4. Install dependencies
pip install -e .

# 5. Fix macOS permissions for voice mode (IMPORTANT!)
./fix_python_permissions.sh
```

### First Launch

**Option 1: Voice Mode (Recommended)**
```bash
source .venv/bin/activate
chandler-voice
```

**Option 2: CLI Mode**
```bash
source .venv/bin/activate
chandler
```

On first launch, Chandler will ask for your API key and save it automatically.

---

## 🎤 Voice Mode Setup

### Step 1: Install and Fix Permissions

```bash
# Install dependencies
source .venv/bin/activate
pip install -e .

# Fix macOS permissions (CRITICAL!)
./fix_python_permissions.sh

# Reset permission cache
tccutil reset All org.python.python
```

**Why this is needed:** macOS requires apps to declare why they need Speech Recognition access. The fix script adds these declarations to Python.app's Info.plist.

### Step 2: Launch Voice Mode

```bash
source .venv/bin/activate
chandler-voice
```

### Step 3: Grant Permissions

You'll see **two permission dialogs**:

1. **"Python.app would like to access Speech Recognition"**
   - Click **OK**

2. **"Python.app would like to access the Microphone"**
   - Click **OK**

### Step 4: Start Using Voice

The **💬 icon** appears in your menu bar. Voice activation is **automatically enabled**!

- **Say**: "hey chandler"
- **Menu opens**: You can continue speaking OR type a message
- **Get response**: Chandler responds via voice (if voice input) or text (if typed)

### Voice Mode Features

| Feature | Status | Notes |
|---------|--------|-------|
| **Wake word detection** | ✅ Working | Says "chandler" anywhere in phrase |
| **Menu bar UI** | ✅ Working | Icon, status, message preview |
| **Text input** | ✅ Working | Type messages anytime |
| **Voice output (TTS)** | ✅ Working | Uses macOS `say` command |
| **High-precision ASR** | ⏳ Stub | Replace `high_precision_asr.py` with your ASR |

### Menu Bar Controls

Click the 💬 icon to see:

```
💬 Chandler AI Assistant
━━━━━━━━━━━━━━━━━━━━━━━━
🟢 Ready - Listening for wake word
💭 No messages yet
📊 Conversation: 0 messages
━━━━━━━━━━━━━━━━━━━━━━━━
⌨️  Type a Message...
━━━━━━━━━━━━━━━━━━━━━━━━
🔇 Stop Listening
🗑️  Clear Conversation
━━━━━━━━━━━━━━━━━━━━━━━━
ℹ️  About Chandler
❌ Quit
```

### State Indicators

| Icon | State | What's Happening |
|------|-------|------------------|
| 💬 | Idle | Ready for input |
| 🎤 | Listening | Recording your voice |
| 🤔 | Thinking | Processing with Claude |
| 🗣️ | Speaking | Speaking response (voice mode) |
| ⚠️ | Error | Something went wrong |

### Customizing Voice Mode

Edit `chandler/config.yaml`:

```yaml
voice_mode:
  wake_word: "chandler"  # Change to any word you want

  high_precision_asr:
    timeout: 30  # Recording timeout in seconds
    silence_threshold: 2.0  # Seconds of silence to stop

  tts:
    voice: "Samantha"  # macOS voice name
    rate: 200  # Words per minute
```

**Available macOS voices:** Run `say -v ?` to see all options.

### Implementing High-Precision ASR

The wake word works, but full voice input requires implementing the ASR stub.

**Edit `chandler/high_precision_asr.py`** and replace with your preferred ASR:

**Option A: OpenAI Whisper**
```python
import openai

def transcribe_audio(timeout=30.0, silence_threshold=2.0, cancel_event=None):
    # Record audio
    audio_data = record_audio(timeout, silence_threshold, cancel_event)

    # Transcribe
    with open("/tmp/recording.wav", "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)

    return transcript["text"]
```

**Option B: Deepgram**
```python
from deepgram import Deepgram

def transcribe_audio(timeout=30.0, silence_threshold=2.0, cancel_event=None):
    dg_client = Deepgram(DEEPGRAM_API_KEY)
    # Stream and transcribe
    return transcript
```

See `VOICE_MODE.md` for complete implementation details.

---

## ⌨️ CLI Mode

### Launch

```bash
source .venv/bin/activate
chandler
```

### Commands

| Command | Description |
|---------|-------------|
| `/help` | Show available commands |
| `/memory` | Show stored memories |
| `/clear` | Clear conversation history |
| `/quit` | Exit Chandler |

### Example Session

```
You: hi
Chandler: Hey! Could I BE any more ready to help you? What's up?

You: what's the weather in San Francisco?
🔍 web_search(query="San Francisco weather")
Chandler: It's currently 65°F and partly cloudy in San Francisco...

You: /quit
```

---

## 🔧 Configuration

### API Key (Required)

**Three ways to set your API key:**

1. **Environment variable** (highest priority):
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

2. **User config file** `~/.chandler/config.yaml`:
   ```yaml
   anthropic_api_key: "sk-ant-..."
   ```

3. **First-launch prompt**: Chandler will ask and save it automatically.

### Full Configuration

Create or edit `~/.chandler/config.yaml`:

```yaml
# API Settings
anthropic_api_key: "sk-ant-..."
anthropic_base_url: "https://api.anthropic.com"
claude_model: "claude-sonnet-4-20250514"
max_tokens: 4096
api_timeout: 300  # 5 minutes

# Vision Model (for computer_use tool)
vision_model:
  api_key: "your-openai-key"
  base_url: "https://api.openai.com/v1"
  model_name: "gpt-4o"

# Safety
allowed_directories:
  - "~"
safety:
  require_confirmation_for_destructive: true
  require_confirmation_for_computer_control: true

# Computer Control
computer_control:
  max_iterations: 15
  timeout: 180
  screenshot_max_size: 1280

# Memory
memory:
  max_conversation_summaries: 50

# Voice Mode
voice_mode:
  enabled: true
  wake_word: "chandler"

  high_precision_asr:
    timeout: 30
    silence_threshold: 2.0

  tts:
    voice: "Samantha"
    rate: 200
```

---

## 🛠️ Available Tools

Chandler has **11 built-in tools** that Claude can use:

| Tool | Description |
|------|-------------|
| 🔍 `web_search` | Search the web via DuckDuckGo |
| 🌐 `web_browse` | Fetch and extract text from web pages |
| 🐍 `run_python` | Execute Python code (sandboxed, 30s timeout) |
| 💻 `run_shell` | Run shell commands (with safety checks) |
| 📖 `read_file` | Read file contents (path-restricted) |
| ✏️ `write_file` | Write to files (path-restricted) |
| 📁 `list_files` | List directory contents |
| 🍎 `system_control` | macOS control (open apps, notifications, volume) |
| 🖱️ `computer_use` | Vision-based GUI automation (requires vision model) |
| 💾 `remember` | Save facts to persistent memory |
| 🧠 `recall` | Search memory for saved facts |

### Tool Examples

**Web Search:**
```
You: what's the latest news about AI?
→ web_search(query="latest AI news")
```

**Code Execution:**
```
You: calculate fibonacci(20)
→ run_python(code="def fib(n): ...")
```

**File Operations:**
```
You: create a hello.txt file with "Hello, World!"
→ write_file(path="~/hello.txt", content="Hello, World!")
```

**macOS Control:**
```
You: open spotify
→ system_control(action="open_app", app_name="Spotify")
```

---

## 🧠 Memory System

Chandler remembers things about you **across sessions**.

### How It Works

- **Automatic**: Claude proactively saves important info (your name, preferences, etc.)
- **Persistent**: Stored in `chandler/data/memory.json`
- **Searchable**: Claude can recall past facts when relevant

### Memory Contents

- **User Profile**: Name, preferences, background
- **Facts**: Anything Claude learns about you
- **Conversation Summaries**: Compressed history of past sessions

### Memory Commands

```
You: remember my favorite color is blue
→ remember(category="preferences", key="favorite_color", value="blue")

You: what's my favorite color?
→ recall(query="favorite color")

You: /memory
→ Shows all stored memories
```

---

## 🔒 Safety Features

### Command Blocking

- **Dangerous commands** blocked entirely:
  - `rm -rf /`, `mkfs`, fork bombs, system file deletion

- **Destructive commands** require confirmation:
  - `rm`, `sudo`, `kill`, `chmod`, `dd`

### Path Restrictions

- File operations restricted to `allowed_directories`
- Default: Only your home directory (`~`)
- Prevents access to system files

### Sandboxing

- **Python code**: Runs in subprocess with 30-second timeout
- **Computer control**: Requires explicit user approval
- **API timeout**: All Claude API calls timeout after 5 minutes

---

## 📁 Project Structure

```
chandler/
├── README.md                    # This file
├── VOICE_MODE.md                # Detailed voice mode docs
├── PERMISSION_FIX.md            # Permission troubleshooting
├── WAKE_WORD_USAGE.md           # Wake word usage guide
├── fix_python_permissions.sh   # Permission fix script
├── setup.py                     # Package setup
├── requirements.txt             # Dependencies
│
├── chandler/
│   ├── __init__.py
│   ├── main.py                  # CLI entry point
│   ├── menu_bar_app.py          # Voice mode entry point
│   ├── brain.py                 # Claude API client
│   ├── config.py                # Config loader
│   ├── config.yaml              # Default config
│   ├── memory.py                # Memory system
│   ├── safety.py                # Safety checks
│   ├── ui.py                    # CLI UI (Rich)
│   ├── voice_ui.py              # Voice mode UI adapter
│   ├── voice_controller.py      # Voice orchestration
│   ├── wake_word_asr.py         # Wake word detection
│   ├── high_precision_asr.py    # ASR stub (user implements)
│   ├── tts_stub.py              # TTS interface
│   ├── computer_control.py      # GUI automation
│   │
│   ├── data/
│   │   └── memory.json          # Persistent memory
│   │
│   └── tools/
│       ├── __init__.py          # Tool registry
│       ├── web_search.py
│       ├── web_browse.py
│       ├── run_python.py
│       ├── run_shell.py
│       ├── file_ops.py
│       ├── system_control.py
│       ├── computer_use.py
│       └── memory_tools.py
```

---

## 🐛 Troubleshooting

### Voice Mode Issues

**Crash on launch:**
```bash
# Run the permission fix
./fix_python_permissions.sh

# Reset TCC cache
tccutil reset All org.python.python

# Try again
chandler-voice
```

**Wake word not detecting:**
- Check if "Start Listening" is enabled (it auto-starts)
- Look for 🟢 "Ready - Listening for wake word" in menu
- Check logs: `tail -f /tmp/chandler_voice.log`

**Permission denied:**
- Open System Settings > Privacy & Security > Microphone
- Enable Python.app
- Open System Settings > Privacy & Security > Speech Recognition
- Enable Speech Recognition

### CLI Mode Issues

**API errors:**
- Check API key: `echo $ANTHROPIC_API_KEY` or check `~/.chandler/config.yaml`
- Verify API access: `curl https://api.anthropic.com/v1/messages -H "x-api-key: YOUR_KEY"`

**Tool execution fails:**
- Check allowed directories in config
- For computer_use: Configure vision model
- For shell commands: Check safety settings

### General Issues

**Import errors:**
```bash
# Reinstall dependencies
source .venv/bin/activate
pip install -e .
```

**Memory issues:**
```bash
# Reset memory
rm chandler/data/memory.json
```

---

## 📚 Documentation

- **`VOICE_MODE.md`** - Complete voice mode documentation
- **`PERMISSION_FIX.md`** - Permission troubleshooting guide
- **`WAKE_WORD_USAGE.md`** - Wake word usage and customization

---

## 🎯 Usage Tips

### Voice Mode

1. **Keep it running**: Leave chandler-voice open in background
2. **Say "hey chandler"**: Works anytime, anywhere
3. **Mix voice & text**: Use wake word OR type messages
4. **Check status**: Icon shows current state

### CLI Mode

1. **Conversational**: Talk naturally, Claude understands context
2. **Tool hints**: Say "search for..." or "run..." to trigger tools
3. **Memory**: Mention your name once, Claude remembers
4. **Quick launch**: Add alias to `~/.zshrc` for instant access

### Best Practices

- **Be specific**: "Search for Python tutorials" vs "search"
- **Use memory**: Let Claude remember your preferences
- **Safety first**: Review destructive commands before confirming
- **Check logs**: `/tmp/chandler_voice.log` for voice mode debugging

---

## 🚀 Quick Reference

### Launch Commands

```bash
# Voice mode
source .venv/bin/activate && chandler-voice

# CLI mode
source .venv/bin/activate && chandler

# Check installation
which chandler
which chandler-voice
```

### Permission Fix

```bash
./fix_python_permissions.sh
tccutil reset All org.python.python
```

### Configuration

```bash
# Edit config
nano ~/.chandler/config.yaml

# View memory
cat chandler/data/memory.json

# View logs
tail -f /tmp/chandler_voice.log
```

---

## 📄 License

MIT License - Use freely, modify as needed.

---

## 🎉 You're Ready!

**CLI Mode:**
```bash
source .venv/bin/activate
chandler
```

**Voice Mode:**
```bash
./fix_python_permissions.sh
source .venv/bin/activate
chandler-voice
# Say "hey chandler" 🎤
```

Enjoy your AI assistant! 💬✨
