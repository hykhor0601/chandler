# Chandler Voice Mode

Voice-activated menu bar app for Chandler, providing a "Hey Siri"-like experience on macOS.

## Features

- 🎤 **Voice Activation**: Say "hey chandler" to wake up the assistant
- 💬 **Menu Bar Interface**: Always-visible icon with dropdown conversation view
- ⌨️ **Multi-modal Input**: Support both voice and text input in the same conversation
- 🗣️ **Smart Response Routing**: Voice input → spoken response, text input → silent response
- 🔋 **Dual ASR System**: Low-power wake word detection + high-precision transcription
- 🧠 **Unified Context**: All messages (voice + text) share the same conversation history

## Quick Start

### 1. Install Dependencies

```bash
# Activate virtual environment
source .venv/bin/activate

# Install (already done if you ran pip install -e .)
pip install -e .
```

### 2. Launch Menu Bar App

```bash
chandler-voice
```

The Chandler icon (💬) will appear in your menu bar.

### 3. Start Listening

Click the menu bar icon → "Start Listening"

The icon will change to indicate the app is ready to receive wake words.

### 4. Interact

Two ways to interact:

**Option 1: Voice**
- Say "hey chandler" or any phrase containing "chandler"
- Menu opens, icon changes to 🎤 (listening)
- Speak your message (30-second timeout)
- Chandler processes and speaks response

**Option 2: Text**
- Click menu bar icon → "Type Message..."
- Enter your message in the dialog
- Chandler processes silently (response shown in menu only)

## Architecture

```
┌─────────────────────────────────────────┐
│      Menu Bar Icon & Controls          │
│  - State indicators (💬🎤🤔🗣️⚠️)      │
│  - Conversation view (recent messages)  │
│  - Text input dialog                    │
└────────────┬────────────────────────────┘
             │
             v
┌─────────────────────────────────────────┐
│       Voice Controller                  │
│  - Coordinates ASR → Brain → TTS        │
│  - Tracks input mode (voice vs text)    │
│  - Routes responses appropriately       │
└──┬───────────────┬─────────────────┬────┘
   │               │                 │
   v               v                 v
┌────────┐  ┌──────────────┐  ┌───────────┐
│ Wake   │  │ High-Prec    │  │ TTS       │
│ Word   │  │ ASR          │  │ (macOS    │
│ (Apple │  │ (user stub)  │  │ 'say')    │
│ Speech)│  │ 30s timeout  │  │           │
└────────┘  └──────────────┘  └───────────┘
                │
                v
          ┌──────────────┐
          │ Brain.chat() │
          │ (unchanged)  │
          └──────────────┘
```

## Configuration

Edit `chandler/config.yaml`:

```yaml
voice_mode:
  enabled: true
  wake_word: "chandler"

  # Wake word detection (low-power)
  wake_word_asr:
    provider: "apple_speech"
    confidence_threshold: 0.7

  # High-precision transcription (LLM-driven)
  high_precision_asr:
    provider: "user_stub"  # Replace with your ASR!
    timeout: 30
    silence_threshold: 2.0

  # Text-to-speech
  tts:
    voice: "Samantha"  # macOS voice
    rate: 200          # Words per minute
    use_built_in: true
```

## Customization

### Replace ASR Modules

The default implementation uses **stub modules** that need to be replaced with real ASR services.

#### 1. Wake Word Detection (`chandler/wake_word_asr.py`)

Current: Stub implementation
Replace with: Apple Speech framework

```python
from Speech import SFSpeechRecognizer
from AVFoundation import AVAudioEngine

class WakeWordDetector:
    def __init__(self, wake_word: str = "chandler"):
        self.recognizer = SFSpeechRecognizer.alloc().init()
        self.audio_engine = AVAudioEngine.alloc().init()
        # ... implement continuous recognition
```

#### 2. High-Precision ASR (`chandler/high_precision_asr.py`)

Current: Stub implementation
Replace with: Your preferred LLM-driven ASR

**Option A: OpenAI Whisper API**
```python
import openai

def transcribe_audio(timeout=30.0, silence_threshold=2.0, cancel_event=None):
    # Record audio
    audio_data = record_audio(timeout, silence_threshold, cancel_event)

    # Transcribe with Whisper
    with open("/tmp/recording.wav", "rb") as f:
        transcript = openai.Audio.transcribe("whisper-1", f)

    return transcript["text"]
```

**Option B: Deepgram**
```python
from deepgram import Deepgram

def transcribe_audio(timeout=30.0, silence_threshold=2.0, cancel_event=None):
    dg_client = Deepgram(API_KEY)
    # Stream audio to Deepgram
    # ...
    return transcript
```

**Option C: AssemblyAI**
```python
import assemblyai as aai

def transcribe_audio(timeout=30.0, silence_threshold=2.0, cancel_event=None):
    transcriber = aai.Transcriber()
    # Record and transcribe
    # ...
    return transcript.text
```

#### 3. TTS (`chandler/tts_stub.py`)

Current: Uses macOS `say` command (works out of box)
Optionally replace with: OpenAI TTS, ElevenLabs, Azure Speech, etc.

```python
import openai

def speak(text, voice=None, rate=None):
    response = openai.Audio.create_speech(
        model="tts-1",
        voice=voice or "alloy",
        input=text,
    )
    response.stream_to_file("/tmp/speech.mp3")
    playsound("/tmp/speech.mp3")
```

## State Machine

The menu bar icon shows the current state:

| Icon | State | Description |
|------|-------|-------------|
| 💬 | Idle | Listening for wake word |
| 🎤 | Listening | Wake word detected, waiting for voice/text |
| 🤔 | Thinking | Processing request through Brain |
| 🗣️ | Speaking | Speaking response (voice mode only) |
| ⌨️ | Typing | Text mode response (silent) |
| ⚠️ | Error | Something went wrong |

## Dual ASR System

### Why Two ASR Systems?

1. **Wake Word Detection** (Low Power)
   - Uses Apple's on-device Speech framework
   - Runs continuously with minimal battery drain
   - No API costs
   - Only detects "chandler" keyword

2. **High-Precision Transcription** (High Accuracy)
   - Uses external LLM-driven ASR (user-provided)
   - Activated only after wake word
   - High accuracy for full sentences
   - Auto-cancels after 30 seconds of silence
   - User can cancel by typing instead

### Input Mode Routing

```
User says "hey chandler"
  → Wake word detected
  → Menu opens + High-precision ASR starts
  → User continues speaking
    → Voice input captured
    → Brain processes
    → TTS speaks response ✓
    → Shown in menu view

User says "hey chandler"
  → Wake word detected
  → Menu opens + High-precision ASR starts
  → User types in text field instead
    → ASR cancelled
    → Text input captured
    → Brain processes
    → Silent response (menu only) ✓
```

## Conversation Context

All messages (voice + text) are stored in the same Brain conversation history:

```
[User (voice)]: "What's the weather?"
[Assistant (voice)]: "It's sunny, 72°F..."

[User (text)]: "What about tomorrow?"
[Assistant (text)]: "Tomorrow will be cloudy..."

Brain maintains full context across input modes!
```

## Troubleshooting

### Icon doesn't appear in menu bar
- Check if app is running: `ps aux | grep chandler-voice`
- Try restarting: Kill process and run `chandler-voice` again

### Wake word not detected
- **Expected**: Wake word detection is a STUB by default
- You need to replace `chandler/wake_word_asr.py` with actual Speech framework code
- For testing, you can trigger manually via menu: "Type Message..."

### High-precision ASR times out
- **Expected**: ASR is a STUB that returns placeholder text after 5 seconds
- Replace `chandler/high_precision_asr.py` with your LLM-driven ASR
- Default timeout is 30 seconds (configurable)

### TTS not working
- Default uses macOS `say` command
- Test: `say "Hello from Chandler"`
- If that works, TTS should work in voice mode
- Check logs: `tail -f /tmp/chandler_voice.log`

### Brain not responding
- Check API key in `config.yaml`
- Check logs for errors
- Test CLI mode first: `chandler` (should work if voice mode works)

## Logs

Voice mode logs to:
- `/tmp/chandler_voice.log` (file)
- Console output (terminal where you ran `chandler-voice`)

```bash
# Follow logs
tail -f /tmp/chandler_voice.log
```

## Backward Compatibility

The original CLI mode is **completely unchanged**:

```bash
# CLI mode (terminal REPL)
chandler

# Voice mode (menu bar app)
chandler-voice
```

Both modes share the same Brain logic, tools, and configuration.

## Development

### Testing Components

```bash
source .venv/bin/activate

# Test Brain with voice UI adapter
python -c "
from chandler.voice_ui import VoiceUIAdapter
from chandler.brain import Brain

ui = VoiceUIAdapter(lambda s, m: print(f'State: {s}'))
brain = Brain(ui_adapter=ui)
print('Brain with voice UI:', brain.ui)
"

# Test voice controller
python -c "
from chandler.voice_controller import VoiceController

vc = VoiceController(
    ui_callback=lambda s, m: print(f'UI: {s} - {m}'),
    message_callback=lambda r, c, m: print(f'Message: {r} ({m}): {c[:50]}')
)
print('Controller initialized, conversation count:', vc.get_conversation_count())
"
```

### Code Structure

```
chandler/
├── brain.py              # Core Brain (modified: +ui_adapter param)
├── ui.py                 # Terminal UI (unchanged)
├── voice_ui.py           # Voice UI adapter (NEW)
├── voice_controller.py   # Voice orchestration (NEW)
├── menu_bar_app.py       # Menu bar app (NEW)
├── wake_word_asr.py      # Wake word detection stub (NEW)
├── high_precision_asr.py # High-precision ASR stub (NEW)
├── tts_stub.py           # TTS interface (NEW)
├── config.yaml           # Config (modified: +voice_mode)
└── config.py             # Config loader (modified: +voice_mode property)
```

## Implementation Stats

- **New Code**: ~1,250 LOC (7 new files)
- **Modified Code**: ~38 LOC (3 files)
- **Brain Logic**: 100% preserved, zero changes to core functionality
- **Backward Compatible**: CLI mode works exactly as before

## Next Steps

1. ✅ **Working Now**: Menu bar app with text input
2. 🔧 **Your Task**: Replace ASR stubs with real implementations
3. 🎯 **Optional**: Customize TTS (default macOS `say` works)
4. 🚀 **Launch**: Run `chandler-voice` and start using!

## Credits

Built with Claude Sonnet 4.5
