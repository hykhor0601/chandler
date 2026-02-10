"""Menu bar app for Chandler voice mode.

Provides:
- Menu bar icon with state indicators
- In-menu conversation view (scrollable chat history)
- Text input field for typing messages
- Manual controls (start/stop listening, clear, quit)
"""

import sys
import signal
import atexit
import logging
from typing import List, Tuple

try:
    import rumps
except ImportError:
    print("Error: rumps not installed. Install with: pip install rumps")
    sys.exit(1)

try:
    from Foundation import NSMakeRect, NSObject
    from AppKit import (
        NSScrollView, NSTextView, NSTextField, NSButton, NSView,
        NSMakePoint, NSMakeSize, NSTextAlignment,
        NSColor, NSFont, NSAttributedString,
        NSBezelBorder, NSMenu, NSMenuItem,
    )
except ImportError:
    print("Error: PyObjC not installed. Should be included in Python 3.13 on macOS.")
    sys.exit(1)

from chandler.voice_controller import VoiceController
from chandler.memory import memory
from chandler import wake_word_asr

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# Icon states
ICONS = {
    "idle": "💬",
    "listening": "🎤",
    "thinking": "🤔",
    "speaking": "🗣️",
    "typing": "⌨️",
    "error": "⚠️",
}


class ConversationView:
    """Custom view for displaying conversation history.

    Shows scrollable chat history with messages formatted as:
    🎤 user: [voice message]
    🗣️ assistant: [voice response]
    ⌨️ user: [text message]
    💬 assistant: [text response]
    """

    def __init__(self, width: int = 400, height: int = 300):
        """Initialize conversation view.

        Args:
            width: View width in pixels
            height: View height in pixels
        """
        # Create scroll view
        self.scroll_view = NSScrollView.alloc().initWithFrame_(
            NSMakeRect(0, 0, width, height)
        )
        self.scroll_view.setHasVerticalScroller_(True)
        self.scroll_view.setAutohidesScrollers_(True)
        self.scroll_view.setBorderType_(NSBezelBorder)

        # Create text view
        self.text_view = NSTextView.alloc().initWithFrame_(
            NSMakeRect(0, 0, width - 20, height)
        )
        self.text_view.setEditable_(False)
        self.text_view.setSelectable_(True)
        self.text_view.setFont_(NSFont.systemFontOfSize_(12))
        self.text_view.setTextColor_(NSColor.whiteColor())
        self.text_view.setBackgroundColor_(NSColor.colorWithWhite_alpha_(0.1, 1.0))

        # Set up scroll view
        self.scroll_view.setDocumentView_(self.text_view)

        # Message history
        self.messages: List[Tuple[str, str, str]] = []  # (role, content, mode)

    def append_message(self, role: str, content: str, mode: str):
        """Append message to conversation view.

        Args:
            role: "user" or "assistant"
            content: Message text
            mode: "voice" or "text"
        """
        # Choose icon based on role and mode
        if role == "user":
            icon = "🎤" if mode == "voice" else "⌨️"
        else:  # assistant
            icon = "🗣️" if mode == "voice" else "💬"

        # Format message
        formatted = f"{icon} {role}: {content}\n\n"

        # Add to history
        self.messages.append((role, content, mode))

        # Update text view
        current_text = self.text_view.string() or ""
        self.text_view.setString_(current_text + formatted)

        # Scroll to bottom
        self.scroll_to_bottom()

    def clear(self):
        """Clear all messages."""
        self.messages = []
        self.text_view.setString_("")

    def scroll_to_bottom(self):
        """Scroll to bottom of text view."""
        text_length = len(self.text_view.string() or "")
        self.text_view.scrollRangeToVisible_((text_length, 0))

    def get_view(self) -> NSScrollView:
        """Get the NSScrollView for embedding in menu.

        Returns:
            NSScrollView instance
        """
        return self.scroll_view


class ChandlerMenuBarApp(rumps.App):
    """Menu bar app for Chandler voice assistant."""

    def __init__(self):
        """Initialize menu bar app."""
        # Note: rumps icon parameter expects a file path or None
        # We'll set the title to include emoji instead
        super().__init__(
            name="Chandler",
            title=ICONS["idle"],  # Use title for emoji icon
            icon=None,  # No image icon
            quit_button=None,  # Custom quit handler
        )

        # Voice controller
        self.controller = VoiceController(
            ui_callback=self.update_state,
            message_callback=self.add_message,
        )

        # State
        self.is_listening = False
        self.current_state = "idle"

        # Build menu
        self._build_menu()

        logger.info("Chandler menu bar app initialized")

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers()

        # Auto-start wake word detection
        self._auto_start_listening()

    def _build_menu(self):
        """Build menu structure with improved UI."""
        # Header with branding
        self.header_item = rumps.MenuItem("💬 Chandler AI Assistant", callback=None)

        # Status with emoji
        self.status_item = rumps.MenuItem("🟢 Ready - Listening for wake word", callback=None)

        # Recent conversation preview
        self.conversation_item = rumps.MenuItem("💭 No messages yet", callback=None)

        # Conversation turn counter
        self.turn_counter = rumps.MenuItem("📊 Conversation: 0 turns", callback=None)

        # Text input with better label
        self.text_input_item = rumps.MenuItem(
            "⌨️  Type a Message...",
            callback=self.show_text_input_dialog
        )

        # Controls
        self.listening_toggle = rumps.MenuItem(
            "🔇 Stop Listening",  # Default to "Stop" since we auto-start
            callback=self.toggle_listening
        )

        self.clear_item = rumps.MenuItem(
            "🗑️  Clear Conversation",
            callback=self.clear_conversation
        )

        # Build menu with better organization
        self.menu = [
            self.header_item,
            rumps.separator,
            self.status_item,
            self.conversation_item,
            self.turn_counter,
            rumps.separator,
            self.text_input_item,
            rumps.separator,
            self.listening_toggle,
            self.clear_item,
            rumps.separator,
            rumps.MenuItem("ℹ️  About Chandler", callback=self.show_about),
            rumps.MenuItem("❌ Quit", callback=self.quit_app),
        ]

    def _auto_start_listening(self):
        """Auto-start wake word detection on launch."""
        logger.info("Auto-starting wake word detection...")

        # Request permissions
        if not wake_word_asr.request_permissions():
            logger.warning("Permissions not granted - wake word detection disabled")
            rumps.notification(
                title="Chandler - Permissions Needed",
                subtitle="Microphone access required",
                message="Grant permissions in System Settings to enable wake word detection.",
                sound=False,
            )
            self.status_item.title = "⚠️  Permissions needed - Click to enable"
            self.listening_toggle.title = "🎤 Enable Wake Word"
            return

        # Start listening
        try:
            self.controller.start_listening()
            self.is_listening = True
            self.listening_toggle.title = "🔇 Stop Listening"
            logger.info("Wake word detection started automatically")

            # Show notification
            rumps.notification(
                title="Chandler Active",
                subtitle="Say 'hey chandler' to activate",
                message="Listening for wake word...",
                sound=False,
            )

        except Exception as e:
            logger.error(f"Failed to auto-start listening: {e}", exc_info=True)
            self.status_item.title = f"⚠️  Error: {str(e)[:30]}"
            self.listening_toggle.title = "🎤 Start Listening"

    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        def shutdown_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down gracefully...")
            self._cleanup()
            sys.exit(0)

        # Register signal handlers
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        # Fallback: atexit handler
        atexit.register(self._cleanup)

    def _cleanup(self):
        """Cleanup resources before exit."""
        try:
            logger.info("Cleaning up resources...")

            # Finalize brain session if exists
            if hasattr(self.controller, 'brain') and self.controller.brain:
                self.controller.brain.finalize_session()

            # Stop fact worker
            memory.fact_worker.stop()

            logger.info("Cleanup complete")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)

    def update_state(self, state: str, message: str = ""):
        """Update menu bar state (called by VoiceController).

        Args:
            state: State name (idle, listening, thinking, speaking, error)
            message: Optional status message
        """
        logger.info(f"State update: {state} - {message}")
        self.current_state = state

        # Update menu bar icon (title)
        self.title = ICONS.get(state, ICONS["idle"])

        # Update status item with emoji and better formatting
        status_emoji = {
            "idle": "🟢",
            "listening": "🎤",
            "thinking": "🤔",
            "speaking": "🗣️",
            "typing": "⌨️",
            "error": "🔴",
        }

        emoji = status_emoji.get(state, "🟢")
        status_text = f"{emoji} {state.capitalize()}"
        if message:
            status_text += f" - {message}"

        self.status_item.title = status_text

    def add_message(self, role: str, content: str, mode: str):
        """Add message to conversation view (called by VoiceController).

        Args:
            role: "user" or "assistant"
            content: Message text
            mode: "voice" or "text"
        """
        logger.info(f"Adding message: {role} ({mode}): {content[:50]}...")

        # Update conversation menu item with last message
        if role == "user":
            icon = "🎤" if mode == "voice" else "👤"
            label = "You"
        else:
            icon = "🗣️" if mode == "voice" else "🤖"
            label = "Chandler"

        preview = content[:45] + "..." if len(content) > 45 else content
        self.conversation_item.title = f"{icon} {label}: {preview}"

        # Update turn counter
        turn_count = self.controller.get_conversation_count()
        self.turn_counter.title = f"📊 Conversation: {turn_count} messages"

    def toggle_listening(self, sender):
        """Toggle wake word listening."""
        if self.is_listening:
            # Stop listening
            self.controller.stop_listening()
            self.is_listening = False
            sender.title = "🎤 Start Listening"
            self.status_item.title = "🔴 Stopped - Wake word disabled"
            logger.info("Stopped listening")

            rumps.notification(
                title="Chandler Paused",
                subtitle="Wake word detection disabled",
                message="Click 'Start Listening' to resume",
                sound=False,
            )
        else:
            # Request permissions first
            logger.info("Requesting microphone and speech recognition permissions...")
            if not wake_word_asr.request_permissions():
                rumps.alert(
                    title="Permission Required",
                    message=(
                        "Chandler needs microphone and speech recognition permissions.\n\n"
                        "Please grant in:\n"
                        "System Settings > Privacy & Security > Microphone\n"
                        "System Settings > Privacy & Security > Speech Recognition"
                    ),
                )
                return

            # Start listening
            try:
                self.controller.start_listening()
                self.is_listening = True
                sender.title = "🔇 Stop Listening"
                self.status_item.title = "🟢 Ready - Listening for wake word"
                logger.info("Started listening")

                rumps.notification(
                    title="Chandler Active",
                    subtitle="Say 'hey chandler' to activate",
                    message="Listening for wake word...",
                    sound=False,
                )
            except Exception as e:
                logger.error(f"Failed to start listening: {e}", exc_info=True)
                rumps.alert(
                    title="Error Starting Wake Word Detection",
                    message=f"{str(e)}\n\nCheck /tmp/chandler_voice.log for details.",
                )

    def show_text_input_dialog(self, sender):
        """Show dialog for text input.

        rumps doesn't support inline text fields, so we use a dialog.
        """
        # Use rumps window to get text input
        response = rumps.Window(
            title="💬 Message Chandler",
            message="What would you like to ask?",
            default_text="",
            ok="Send",
            cancel="Cancel",
            dimensions=(400, 180)
        ).run()

        if response.clicked:
            text = response.text
            if text and text.strip():
                logger.info(f"Text input from dialog: '{text[:50]}...'")

                # Show brief notification
                rumps.notification(
                    title="Processing...",
                    subtitle="Chandler is thinking",
                    message=text[:50] + ("..." if len(text) > 50 else ""),
                    sound=False,
                )

                self.controller.process_text_input(text)
            else:
                logger.debug("Empty text input, ignoring")

    def clear_conversation(self, sender):
        """Clear conversation history."""
        # Confirm before clearing
        response = rumps.alert(
            title="Clear Conversation?",
            message="This will erase all conversation history.",
            ok="Clear",
            cancel="Cancel",
        )

        if response == 1:  # OK clicked
            self.controller.clear_conversation()
            self.conversation_item.title = "💭 No messages yet"
            self.turn_counter.title = "📊 Conversation: 0 messages"
            logger.info("Conversation cleared")

            rumps.notification(
                title="Conversation Cleared",
                subtitle="Starting fresh",
                message="All messages have been removed",
                sound=False,
            )

    def show_about(self, sender):
        """Show about dialog."""
        rumps.alert(
            title="💬 Chandler - AI Voice Assistant",
            message=(
                "Voice-activated AI assistant for macOS\n\n"
                "🎤 Say 'hey chandler' to activate\n"
                "⌨️  Or type messages anytime\n"
                "🧠 Powered by Claude Sonnet 4.5\n"
                "🍎 Uses Apple Speech Framework\n\n"
                "Features:\n"
                "• Web search & browsing\n"
                "• Python code execution\n"
                "• Shell commands\n"
                "• File operations\n"
                "• Computer vision\n"
                "• Memory & context\n\n"
                "Version 1.0"
            ),
        )

    def quit_app(self, sender):
        """Quit application."""
        # Confirm before quitting
        response = rumps.alert(
            title="Quit Chandler?",
            message="Wake word detection will stop.",
            ok="Quit",
            cancel="Cancel",
        )

        if response == 1:  # OK clicked
            logger.info("Quitting Chandler")
            if self.is_listening:
                logger.info("Stopping wake word detection...")
                self.controller.stop_listening()

            # Cleanup before quitting
            self._cleanup()

            rumps.notification(
                title="Chandler Stopped",
                subtitle="Goodbye!",
                message="Wake word detection disabled",
                sound=False,
            )

            rumps.quit_application()


def main():
    """Main entry point for menu bar app."""
    logger.info("Starting Chandler menu bar app...")

    # Check if running on macOS
    if sys.platform != "darwin":
        print("Error: Chandler voice mode requires macOS")
        sys.exit(1)

    # Create and run app
    app = ChandlerMenuBarApp()
    app.run()


if __name__ == "__main__":
    main()
