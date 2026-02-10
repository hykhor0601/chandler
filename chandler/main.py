"""Chandler - Personal AI Assistant entry point."""

import sys
import signal
import atexit

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
import chandler.tools.ai_news         # noqa: F401
import chandler.tools.mode_control    # noqa: F401
import chandler.tools.profile_tools   # noqa: F401


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


def setup_signal_handlers(brain):
    """Setup signal handlers for graceful shutdown.

    Args:
        brain: Brain instance to finalize on shutdown
    """
    def shutdown_handler(signum, frame):
        ui.print_info("\n\nShutting down gracefully... Session saved. Goodbye!")
        brain.finalize_session()
        memory.fact_worker.stop()
        sys.exit(0)

    # Register handlers for SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Fallback: atexit handler
    atexit.register(lambda: brain.finalize_session())


def main():
    """Main REPL loop."""
    _ensure_api_key()

    from chandler.brain import Brain
    brain = Brain()

    # Start a new session
    brain.session_id = memory.start_session()

    # Setup graceful shutdown handlers
    setup_signal_handlers(brain)

    ui.print_welcome()

    while True:
        user_input = ui.get_user_input()

        if not user_input.strip():
            continue

        # Handle commands
        cmd = user_input.strip().lower()
        if cmd in ("/quit", "/exit", "quit", "exit"):
            ui.print_info("Saving session and shutting down...")
            brain.finalize_session()
            memory.fact_worker.stop()
            ui.print_info("Goodbye!")
            break
        elif cmd == "/clear":
            brain.clear_conversation()
            ui.print_info("Conversation cleared.")
            continue
        elif cmd == "/memory":
            ui.print_memory(memory.all_data)
            continue
        elif cmd == "/mode":
            ui.print_info(f"Current mode: {brain.get_mode_status()}")
            continue
        elif cmd == "/profile":
            profile_summary = memory.user_profile.get_summary()
            ui.print_profile(profile_summary)
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
