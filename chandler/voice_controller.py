"""Voice controller - orchestrates ASR, Brain, TTS, and menu bar UI.

This module coordinates:
1. Wake word detection (low-power Apple Speech)
2. High-precision transcription (LLM-driven ASR)
3. Brain processing (agentic tool_use loop)
4. Response routing (voice mode → TTS, text mode → silent)
5. Menu bar state updates
"""

import threading
import logging
from typing import Callable, Optional

from chandler.brain import Brain
from chandler.voice_ui import VoiceUIAdapter
from chandler.memory import memory
from chandler import wake_word_asr
from chandler import high_precision_asr
from chandler import tts_stub

logger = logging.getLogger(__name__)


class VoiceController:
    """Orchestrates voice-activated conversation flow.

    Manages:
    - Dual ASR system (wake word + high-precision)
    - Input mode tracking (voice vs text)
    - Response routing based on input mode
    - Thread-safe state management
    - Menu bar UI updates
    """

    def __init__(
        self,
        ui_callback: Callable[[str, str], None],
        message_callback: Callable[[str, str, str], None],
    ):
        """Initialize voice controller.

        Args:
            ui_callback: Function to update menu bar state
                        Called as ui_callback(state, message)
                        States: idle, listening, thinking, speaking, error
            message_callback: Function to add message to menu conversation view
                            Called as message_callback(role, content, mode)
                            role: "user" or "assistant"
                            mode: "voice" or "text"
        """
        self.ui_callback = ui_callback
        self.message_callback = message_callback

        # UI adapter for Brain
        self.ui_adapter = VoiceUIAdapter(ui_callback)

        # Brain instance with voice UI
        self.brain = Brain(ui_adapter=self.ui_adapter)

        # Start a new session for voice mode
        self.brain.session_id = memory.start_session()

        # Threading
        self._transcription_thread: Optional[threading.Thread] = None
        self._cancel_transcription = threading.Event()
        self._state_lock = threading.Lock()
        self._current_input_mode: Optional[str] = None  # "voice" or "text"
        self._is_processing = False

        # Wake word detector
        self._wake_detector = wake_word_asr.get_detector()

        logger.info("Voice controller initialized")

    def start_listening(self):
        """Start wake word detection (low-power Apple Speech)."""
        logger.info("Starting wake word detection")
        self._wake_detector.start_listening(callback=self._handle_wake_event)
        self._set_state("idle", "Listening for wake word...")

    def stop_listening(self):
        """Stop wake word detection."""
        logger.info("Stopping wake word detection")
        self._wake_detector.stop_listening()
        self._cancel_transcription.set()
        self._set_state("idle", "Stopped")

    def _handle_wake_event(self):
        """Wake word detected - open menu and start listening.

        This is called by wake_word_asr when "chandler" is detected.
        """
        logger.info("Wake word detected!")

        # Don't start new transcription if already processing
        with self._state_lock:
            if self._is_processing:
                logger.info("Already processing, ignoring wake word")
                return
            self._is_processing = True

        # Update state to listening
        self._set_state("listening", "Listening...")

        # Notify menu bar to open dropdown
        # (Menu bar app should show conversation view + text field)

        # Start high-precision ASR in background thread
        self._cancel_transcription.clear()
        self._transcription_thread = threading.Thread(
            target=self._transcribe_with_timeout,
            daemon=True,
        )
        self._transcription_thread.start()

    def _transcribe_with_timeout(self):
        """High-precision ASR with 30-second auto-cancel.

        Runs in background thread. User can switch to text input to cancel.
        """
        try:
            logger.info("Starting high-precision ASR (30s timeout)")

            # Record and transcribe audio
            user_input = high_precision_asr.transcribe_audio(
                timeout=30.0,
                silence_threshold=2.0,
                cancel_event=self._cancel_transcription,
            )

            # Check if cancelled
            if self._cancel_transcription.is_set():
                logger.info("ASR was cancelled (user switched to text)")
                return

            if user_input and user_input.strip():
                logger.info(f"Voice input captured: '{user_input[:50]}...'")
                # Process as voice mode
                self._process_input(user_input, mode="voice")
            else:
                logger.warning("Empty voice input, returning to idle")
                self._set_state("idle", "No speech detected")
                with self._state_lock:
                    self._is_processing = False

        except high_precision_asr.TranscriptionCancelledError:
            logger.info("ASR cancelled by user (switched to text input)")
            with self._state_lock:
                self._is_processing = False

        except high_precision_asr.TranscriptionTimeoutError:
            logger.warning("ASR timeout - no speech detected within 30 seconds")
            self._set_state("idle", "Timeout - no speech detected")
            with self._state_lock:
                self._is_processing = False

        except Exception as e:
            logger.error(f"ASR error: {e}", exc_info=True)
            self._set_state("error", f"ASR error: {str(e)}")
            with self._state_lock:
                self._is_processing = False

    def process_text_input(self, text: str):
        """User submitted text from menu bar field.

        Args:
            text: User's text input
        """
        if not text or not text.strip():
            logger.warning("Empty text input received")
            return

        logger.info(f"Text input received: '{text[:50]}...'")

        # Cancel any ongoing voice transcription
        self._cancel_transcription.set()

        # Process as text mode
        self._process_input(text, mode="text")

    def _process_input(self, user_input: str, mode: str):
        """Process user input through Brain and route response.

        Args:
            user_input: User's input text (from voice or text)
            mode: Input mode ("voice" or "text")
        """
        try:
            # Track input mode
            with self._state_lock:
                self._current_input_mode = mode

            # Add user message to menu view
            self.message_callback("user", user_input, mode)

            # State: THINKING
            self._set_state("thinking", "Processing...")

            # Process through Brain (blocks until done)
            logger.info(f"Sending to Brain: '{user_input[:50]}...'")
            response = self.brain.chat(user_input)
            logger.info(f"Brain response: '{response[:50]}...'")

            # Add assistant response to menu view
            self.message_callback("assistant", response, mode)

            # Route response based on input mode
            if mode == "voice":
                # Voice mode: speak response
                logger.info("Voice mode - speaking response")
                self._set_state("speaking", "Speaking...")
                tts_stub.speak(response)
                self._set_state("idle", "Listening for wake word...")
            else:
                # Text mode: silent (already in menu view)
                logger.info("Text mode - silent response")
                self._set_state("idle", "Listening for wake word...")

        except Exception as e:
            logger.error(f"Error processing input: {e}", exc_info=True)
            self._set_state("error", f"Error: {str(e)}")

        finally:
            # Reset processing flag
            with self._state_lock:
                self._is_processing = False
                self._current_input_mode = None

    def _set_state(self, state: str, message: str = ""):
        """Update menu bar state.

        Args:
            state: State name (idle, listening, thinking, speaking, error)
            message: Optional status message
        """
        logger.debug(f"State change: {state} - {message}")
        self.ui_callback(state, message)

    def clear_conversation(self):
        """Clear conversation history."""
        logger.info("Clearing conversation")
        self.brain.clear_conversation()
        self._set_state("idle", "Conversation cleared")

    def get_conversation_count(self) -> int:
        """Get number of conversation turns.

        Returns:
            Number of messages in conversation
        """
        return len(self.brain.conversation)

    def is_processing(self) -> bool:
        """Check if currently processing input.

        Returns:
            True if processing, False otherwise
        """
        with self._state_lock:
            return self._is_processing
