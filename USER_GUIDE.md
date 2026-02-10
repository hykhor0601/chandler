# 📖 Chandler User Guide

Complete guide to using Chandler - your AI assistant with personality!

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Features](#features)
4. [Commands](#commands)
5. [Tips & Tricks](#tips--tricks)

---

## Getting Started

### First Time Setup

1. **Install Chandler** (see README.md)
2. **Start CLI mode**: `chandler`
3. **Chandler will introduce itself and ask for your name**
4. **Chat naturally** - that's it!

### Your First Conversation

```
You: Hey!

Chandler: Hey! I'm Chandler, your AI assistant. Nice to meet you!
          What's your name?

You: I'm Alex

Chandler: Great to meet you, Alex! So what brings you here today?
```

Chandler will automatically remember everything you share!

---

## Basic Usage

### CLI Mode

```bash
chandler
```

**Talk naturally:**
- Ask questions
- Request help with tasks
- Share information about yourself
- Get AI news and updates

**Chandler remembers:**
- Your name, occupation, location
- Your interests and hobbies
- Your pets and family
- Your current projects
- Your tech stack
- Your preferences

---

## Features

### 🧠 Two Intelligent Modes

Chandler automatically switches between modes based on your question:

**👋 Buddy Mode** (Default)
- Quick, casual, friendly responses
- Perfect for daily tasks and simple questions
- Fast responses

**🔬 Research Mode** (Auto-activates)
- Deep, thorough analysis
- Extended thinking (15k token budget)
- Automatically activates for complex questions
- Returns to Buddy Mode when done

**Example:**
```
You: Hey, what's 2+2?
[Stays in Buddy Mode - quick answer]

You: Explain the mathematical theory behind transformer attention
[🔬 Switches to Research Mode - deep analysis]

You: Thanks!
[👋 Returns to Buddy Mode]
```

---

### 🧑 Comprehensive User Profile

Chandler builds a complete picture of you:

**What Chandler remembers:**
- 👤 **Personal**: Name, age, occupation, location, company
- 🎯 **Interests**: Your hobbies and what you care about
- 🐾 **Pets**: Names, types, breeds
- 👨‍👩‍👧‍👦 **Family**: Spouse, children, parents
- 💼 **Projects**: What you're working on
- 🛠️ **Tech Stack**: Python, PyTorch, React, etc.
- 🎯 **Goals**: What you want to achieve
- ⚙️ **Preferences**: How you like to communicate

**View your profile:**
```bash
chandler
> /profile
```

---

### 🤖 Daily AI News

Stay updated on AI tech news:

```
You: What's the latest AI news?

[Chandler shows:]
- 📈 Trending AI/ML GitHub projects
- 🔥 Top AI stories from Hacker News
- 📄 Latest AI research papers
```

**More options:**
```
You: Show me trending AI projects on GitHub
You: Search GitHub for LLM agents
You: What are the latest AI papers?
```

---

### 🌐 Web & Research

**Web search:**
```
You: Search for best practices in RAG systems
```

**Browse specific URLs:**
```
You: Browse https://example.com and summarize the content
```

**Get AI news:**
```
You: What's trending in AI today?
```

---

### 💻 Code Execution

**Run Python:**
```
You: Calculate the mean of [1, 2, 3, 4, 5] in Python
```

**Run shell commands:**
```
You: List files in the current directory
You: Check my git status
```

**File operations:**
```
You: Read the file config.yaml
You: Write "Hello World" to test.txt
```

---

### 🖥️ macOS System Control

**Control your Mac:**
```
You: Open Safari
You: Set volume to 50%
You: Take a screenshot
```

**Vision-based automation:**
```
You: Click the Submit button in the current window
You: Find and click the Settings icon
```

---

## Commands

### CLI Commands

```
/help      - Show available commands
/profile   - View your complete profile
/memory    - Show stored memories (legacy)
/mode      - Show current mode (Buddy/Research)
/clear     - Clear conversation history
/quit      - Exit Chandler
```

### Example Session

```bash
chandler

You: /help
[Shows command list]

You: /profile
[Shows your complete profile]

You: /mode
Current mode: 👋 Buddy Mode

You: Explain transformer attention in detail
🔬 Switching to Research Mode...
[Detailed explanation]

You: /mode
Current mode: 🔬 Research Mode

You: Thanks!
👋 Back to Buddy Mode

You: /clear
Conversation cleared.

You: /quit
Saving session... Goodbye!
```

---

## Tips & Tricks

### Get Better Responses

**Be specific:**
```
❌ Tell me about ML
✅ Explain how transformer attention mechanisms work
```

**Share context:**
```
✅ I'm building a RAG system with Python and PyTorch.
   How should I handle embedding storage?
```

**Ask follow-ups:**
```
You: What are RAG systems?
Chandler: [Explains RAG]
You: Can you show me a simple implementation?
Chandler: [Provides code]
```

---

### Make Chandler Yours

**Share your info naturally:**
```
You: I'm Sarah, I work as an AI engineer at Google

[Chandler automatically saves:]
- name: Sarah
- occupation: AI Engineer
- company: Google
```

**Tell Chandler your preferences:**
```
You: I prefer brief, direct responses

[Chandler saves and adapts communication style]
```

**Share your interests:**
```
You: I love hiking and photography

[Chandler remembers and references later]
```

---

### Workflow Examples

**Morning Routine:**
```
You: Good morning! What's the AI news today?
Chandler: [Fetches latest AI news]

You: Interesting! Tell me more about that top paper
Chandler: [🔬 Research Mode - deep dive]
```

**Coding Help:**
```
You: I'm stuck on this Python error: [paste error]
Chandler: [Analyzes and suggests fixes]

You: Now explain why that works
Chandler: [🔬 Research Mode - detailed explanation]
```

**Learning Session:**
```
You: I want to learn about transformers

Chandler: [🔬 Research Mode - comprehensive explanation]

You: Can you show me a simple example?

Chandler: [👋 Buddy Mode - practical code]
```

---

### Keyboard Shortcuts

**During conversation:**
- `Ctrl+C` - Exit gracefully (saves session)
- `Ctrl+D` - Also exits
- `↑` / `↓` - Command history (in terminal)

---

### Privacy & Data

**What Chandler stores:**
- Your profile (`chandler/data/user_profile.json`)
- Conversation sessions (`chandler/data/conversations/`)
- Memory facts (`chandler/data/memory.json`)

**All stored locally** - no cloud sync

**To reset:**
```bash
# Clear profile
rm chandler/data/user_profile.json

# Clear sessions
rm -rf chandler/data/conversations/*

# Clear memory
rm chandler/data/memory.json

# Start fresh
chandler
```

---

## Voice Mode

### Quick Start

```bash
chandler-voice
```

**Say:** "Hey Chandler" to activate
**Then:** Ask your question naturally

### Voice Features

- Wake word detection ("Hey Chandler")
- Menu bar icon (💬 Buddy Mode, 🔬 Research Mode)
- Text input available (click icon → Type a Message)
- Spoken responses for voice input
- Silent responses for text input

---

## Troubleshooting

### Web Search Not Working

**If searches fail:**
1. Check internet connection
2. Wait a moment (rate limiting)
3. Try more specific queries
4. Use `web_browse` for specific URLs

### Voice Mode Issues

**See:** `VOICE_MODE.md` for detailed voice setup

**Quick checks:**
1. macOS permissions granted?
2. Microphone working?
3. Check `/tmp/chandler_voice.log`

### Memory Not Saving

**If profile not updating:**
```bash
# Check profile exists
cat chandler/data/user_profile.json

# Check permissions
ls -la chandler/data/

# Restart Chandler
chandler
```

---

## Advanced Usage

### Configure Extended Thinking

Edit `~/.chandler/config.yaml`:

```yaml
extended_thinking:
  enabled: true  # Force extended thinking always
  budget_tokens: 20000  # Increase thinking budget
```

### Customize Mode Behavior

Edit `chandler/modes.py` to adjust:
- When modes switch
- Thinking budgets
- Response styles

### Access Full Profile Programmatically

```python
from chandler.memory import memory

# Get full profile
profile = memory.user_profile.get_full_profile()

# Add custom data
memory.user_profile.add_note("Custom note here")
```

---

## FAQ

**Q: Does Chandler always remember everything?**
A: Yes! Every message is auto-saved. Your profile persists across sessions.

**Q: Can I edit my profile?**
A: Yes! Edit `chandler/data/user_profile.json` directly or use `/profile` command.

**Q: How do I make Chandler forget something?**
A: Edit the JSON files directly or clear specific data files.

**Q: Does Research Mode cost more?**
A: Yes, extended thinking uses more tokens. But it's only used when needed.

**Q: Can I use Chandler without an API key?**
A: No, Anthropic API key is required.

**Q: Is my data private?**
A: Yes, everything is stored locally. No cloud sync.

**Q: How do I update Chandler?**
A: `git pull` in the project directory, then `pip install -e .`

---

## Getting Help

**In Chandler:**
```
You: How do I [task]?
Chandler will explain!
```

**Commands:**
```
/help - In-app help
```

**Documentation:**
- `README.md` - Installation & setup
- `CLAUDE.md` - Development guide
- `VOICE_MODE.md` - Voice setup details

**Report issues:**
- GitHub: [Your repo URL]

---

## Examples Gallery

### Example 1: Personal Assistant

```
You: Remind me - what projects am I working on?

Chandler: Based on your profile, you're working on:
          - RAG System (active)
          - ML Pipeline (active)

          Want to talk about either of these?
```

### Example 2: Learning Assistant

```
You: Explain transformers to me

Chandler: [🔬 Research Mode activated]
          [Comprehensive explanation with examples]

You: Now show me the math

Chandler: [Detailed mathematical breakdown]
```

### Example 3: Coding Partner

```
You: Help me debug this Python error [paste]

Chandler: I see the issue - you're missing...
          [Explanation + fix]

You: Why does that fix it?

Chandler: [🔬 Research Mode - detailed theory]
```

---

## What Makes Chandler Special

✅ **Remembers everything** - Automatic profile building
✅ **Two modes** - Quick answers OR deep research
✅ **AI news** - Stay updated effortlessly
✅ **Personality** - Chandler Bing-inspired wit
✅ **Voice & text** - Use however you prefer
✅ **Smart context** - Only loads relevant info
✅ **Crash-proof** - Never lose conversations (Ctrl+C safe)

---

**Enjoy your smarter assistant! 🤖✨**

Need help? Just ask Chandler!
