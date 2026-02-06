# Chandler — Personal AI Assistant

A text-based personal AI assistant powered by Anthropic Claude. Features persistent memory, web search, code execution, macOS system control, and vision-based GUI automation.

## Requirements

- Python 3.10+
- macOS (for system control and computer vision features)
- [Anthropic API key](https://console.anthropic.com/)

## Setup

```bash
# 1. Clone or copy the project
cd /path/to/chandler

# 2. Create virtual environment
python3 -m venv .venv

# 3. Activate it
source .venv/bin/activate

# 4. Install
pip install -e .
```

## Configuration

### API Key

You have three options (in order of priority):

1. **Environment variable** — set before launching:
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

2. **User config file** — create `~/.chandler/config.yaml`:
   ```yaml
   anthropic_api_key: "sk-ant-..."
   ```

3. **First-launch prompt** — if no key is found, Chandler will ask and save it to `~/.chandler/config.yaml` automatically.

### Base URL

If you use a proxy or alternative Anthropic-compatible endpoint, set the base URL in `~/.chandler/config.yaml`:

```yaml
anthropic_base_url: "https://api.anthropic.com"  # default
```

### Vision Model (optional)

For GUI automation via the `computer_use` tool, configure a vision-capable model in `~/.chandler/config.yaml`:

```yaml
vision_model:
  api_key: "your-openai-or-compatible-key"
  base_url: "https://api.openai.com/v1"
  model_name: "gpt-4o"
```

### Full Config Reference

Create `~/.chandler/config.yaml` to override any defaults:

```yaml
anthropic_api_key: ""
claude_model: "claude-sonnet-4-20250514"
max_tokens: 4096

allowed_directories:
  - "~"

safety:
  require_confirmation_for_destructive: true
  require_confirmation_for_computer_control: true

computer_control:
  max_iterations: 15
  timeout: 180
  screenshot_max_size: 1280
  active_window_only: false

memory:
  max_conversation_summaries: 50
```

## Usage

```bash
# Activate venv and run
source .venv/bin/activate
chandler
```

Or run directly without activating:

```bash
.venv/bin/chandler
```

### Quick Launch Alias (optional)

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias chandler='/path/to/chandler/.venv/bin/chandler'
```

Then just type `chandler` from anywhere.

### Commands

| Command   | Description                  |
|-----------|------------------------------|
| `/help`   | Show available commands      |
| `/memory` | Show stored memories         |
| `/clear`  | Clear conversation history   |
| `/quit`   | Exit Chandler                |

## Available Tools

Chandler has 11 built-in tools that Claude can use:

| Tool | Description |
|------|-------------|
| `web_search` | Search the web via DuckDuckGo |
| `web_browse` | Fetch and extract text from web pages |
| `run_python` | Execute Python code (sandboxed, 30s timeout) |
| `run_shell` | Run shell commands (with safety checks) |
| `read_file` | Read file contents (path-restricted) |
| `write_file` | Write to files (path-restricted) |
| `list_files` | List directory contents |
| `system_control` | macOS control — open apps, notifications, volume, AppleScript |
| `computer_use` | Vision-based GUI automation (requires vision model config) |
| `remember` | Save facts about the user to persistent memory |
| `recall` | Search persistent memory for saved facts |

## Memory

Chandler remembers things about you across sessions. Memory is stored in `chandler/data/memory.json` and includes:

- **User profile** — name, preferences, background
- **Facts** — anything Claude learns about you
- **Conversation summaries** — compressed history of past sessions

Claude proactively saves important info (like your name) without being asked. Use `/memory` to see what's stored.

## Safety

- **Dangerous commands** (e.g. `rm -rf /`, `mkfs`, fork bombs) are blocked entirely
- **Destructive commands** (e.g. `rm`, `sudo`, `kill`) require user confirmation
- **File operations** are restricted to allowed directories (default: `~`)
- **Python code** runs in a subprocess with a 30-second timeout
- **Computer control** requires explicit user approval before executing

## Project Structure

```
chandler/
├── __init__.py
├── main.py               # REPL entry point
├── brain.py              # Claude API client with tool_use agentic loop
├── config.py             # YAML config loader
├── config.yaml           # Default config
├── memory.py             # Persistent JSON memory system
├── safety.py             # Command blocklist, path restrictions
├── ui.py                 # Rich terminal UI
├── computer_control.py   # Vision-based GUI automation
├── data/
│   └── memory.json       # Persistent memory store
└── tools/
    ├── __init__.py        # Tool registry + @tool decorator
    ├── web_search.py
    ├── web_browse.py
    ├── run_python.py
    ├── run_shell.py
    ├── file_ops.py
    ├── system_control.py
    ├── computer_use.py
    └── memory_tools.py
```
