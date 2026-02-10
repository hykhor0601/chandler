"""Voice UI adapter for Chandler - replaces Rich terminal UI in voice mode."""

import logging
from contextlib import contextmanager
from typing import Callable


# Configure logging for voice mode debugging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("/tmp/chandler_voice.log"),
        logging.StreamHandler(),
    ],
)


class NoOpContext:
    """No-op context manager for voice mode (no visual spinner needed)."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class VoiceUIAdapter:
    """UI adapter for voice mode - implements same interface as ui.py.

    Instead of rich terminal output, this logs events and calls state callbacks
    to update the menu bar app UI.
    """

    def __init__(self, state_callback: Callable[[str, str], None]):
        """Initialize voice UI adapter.

        Args:
            state_callback: Function to update menu bar state.
                            Called as state_callback(state, message)
                            where state is one of: idle, listening, thinking, speaking, error
        """
        self.state_callback = state_callback
        self.logger = logging.getLogger("chandler.voice_ui")

    def get_spinner(self, message: str = "Thinking...") -> NoOpContext:
        """Create a no-op spinner context (no visual spinner in voice mode).

        Args:
            message: Status message (logged but not displayed)

        Returns:
            No-op context manager
        """
        self.logger.debug(f"Spinner: {message}")
        # Update menu bar to "thinking" state
        self.state_callback("thinking", message)
        return NoOpContext()

    def print_assistant(self, text: str):
        """Log assistant response (displayed in menu bar separately).

        Args:
            text: Assistant's text response
        """
        self.logger.debug(f"Assistant: {text[:100]}...")

    def print_streaming_text(self, text: str):
        """Log streaming text (not used in voice mode).

        Args:
            text: Streamed text chunk
        """
        self.logger.debug(f"Streaming: {text}")

    def print_tool_call(self, tool_name: str, args: dict):
        """Log tool being called.

        Args:
            tool_name: Name of the tool
            args: Tool arguments
        """
        args_str = ", ".join(f"{k}={repr(v)[:60]}" for k, v in args.items())
        self.logger.info(f"⚙ Tool call: {tool_name}({args_str})")

    def print_tool_result(self, tool_name: str, result: str, max_len: int = 500):
        """Log tool result.

        Args:
            tool_name: Name of the tool
            result: Tool result string
            max_len: Maximum length to log
        """
        display = result[:max_len] + "..." if len(result) > max_len else result
        self.logger.info(f"✓ Tool result: {tool_name} → {display}")

    def print_tool_error(self, tool_name: str, error: str):
        """Log tool error.

        Args:
            tool_name: Name of the tool
            error: Error message
        """
        self.logger.error(f"✗ Tool error: {tool_name} → {error}")
        # Update menu bar to error state
        self.state_callback("error", f"Tool error: {tool_name}")

    def print_error(self, message: str):
        """Log error message.

        Args:
            message: Error message
        """
        self.logger.error(f"Error: {message}")
        self.state_callback("error", message)

    def print_info(self, message: str):
        """Log info message.

        Args:
            message: Info message
        """
        self.logger.info(message)

    def print_warning(self, message: str):
        """Log warning message.

        Args:
            message: Warning message
        """
        self.logger.warning(message)

    def print_memory(self, memory_data: dict):
        """Log memory contents (not displayed in voice mode).

        Args:
            memory_data: Memory data dictionary
        """
        self.logger.debug(f"Memory: {memory_data}")

    def print_help(self):
        """Log help (not used in voice mode)."""
        self.logger.debug("Help requested (voice mode)")

    def get_user_input(self) -> str:
        """Not used in voice mode (input comes from ASR or menu text field).

        Raises:
            NotImplementedError: Voice mode doesn't use this method
        """
        raise NotImplementedError("Voice mode uses ASR or menu text input")
