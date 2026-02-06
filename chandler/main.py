"""Chandler - Personal AI Assistant entry point."""

import sys

from chandler.config import config
from chandler.memory import memory
from chandler import ui

# Import all tool modules to trigger registration via @tool decorators
import chandler.tools.web_search      # noqa: F401
import chandler.tools.web_browse      # noqa: F401
import chandler.tools.run_python      # noqa: F401
import chandler.tools.run_shell       # noqa: F401
import chandler.tools.file_ops        # noqa: F401
import chandler.tools.system_control  # noqa: F401
import chandler.tools.computer_use    # noqa: F401
import chandler.tools.memory_tools    # noqa: F401


def _ensure_api_key():
    """Prompt for API key if not configured."""
    if config.api_key:
        return

    ui.print_warning("No Anthropic API key found.")
    ui.print_info("Set it via ANTHROPIC_API_KEY env var or enter it now.")
    try:
        key = input("Anthropic API key: ").strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit(0)

    if not key:
        ui.print_error("API key is required. Set ANTHROPIC_API_KEY or add to ~/.chandler/config.yaml")
        sys.exit(1)

    config.save_api_key(key)
    ui.print_info("API key saved to ~/.chandler/config.yaml")


def main():
    """Main REPL loop."""
    _ensure_api_key()

    from chandler.brain import Brain
    brain = Brain()

    ui.print_welcome()

    while True:
        user_input = ui.get_user_input()

        if not user_input.strip():
            continue

        # Handle commands
        cmd = user_input.strip().lower()
        if cmd in ("/quit", "/exit", "quit", "exit"):
            ui.print_info("Goodbye!")
            break
        elif cmd == "/clear":
            brain.clear_conversation()
            ui.print_info("Conversation cleared.")
            continue
        elif cmd == "/memory":
            ui.print_memory(memory.all_data)
            continue
        elif cmd == "/help":
            ui.print_help()
            continue

        # Chat with Claude
        try:
            response = brain.chat(user_input)
            ui.print_assistant(response)
        except KeyboardInterrupt:
            ui.print_info("\nInterrupted.")
        except Exception as e:
            ui.print_error(str(e))


if __name__ == "__main__":
    main()
