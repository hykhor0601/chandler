"""Wake word detection using Apple Speech framework (low-power).

This module provides low-power, continuous wake word detection using Apple's
on-device Speech framework. No API costs, minimal battery drain.
"""

import time
import threading
import logging
from typing import Callable, Optional

try:
    from Foundation import NSObject
    from Speech import (
        SFSpeechRecognizer,
        SFSpeechAudioBufferRecognitionRequest,
    )
    from AVFoundation import (
        AVAudioEngine,
        AVAudioSession,
        AVAudioSessionCategoryRecord,
        AVAudioSessionModeDefault,
    )
    SPEECH_AVAILABLE = True
except ImportError as e:
    SPEECH_AVAILABLE = False
    logging.warning(f"Speech framework not available - wake word detection will not work: {e}")
except Exception as e:
    SPEECH_AVAILABLE = False
    logging.error(f"Error importing Speech framework: {e}")

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Continuous wake word detection using Apple Speech API.

    This runs locally on-device with low power consumption.
    No API costs, minimal battery drain.
    """

    def __init__(self, wake_word: str = "chandler"):
        """Initialize wake word detector.

        Args:
            wake_word: The wake word to detect (default: "chandler")
        """
        if not SPEECH_AVAILABLE:
            raise ImportError("Speech framework not available - cannot use wake word detection")

        self.wake_word = wake_word.lower()
        self._is_listening = False
        self._callback: Optional[Callable[[], None]] = None
        self._listen_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

        # Speech recognition components
        self.recognizer = SFSpeechRecognizer.alloc().init()
        self.audio_engine = AVAudioEngine.alloc().init()
        self.recognition_request = None
        self.recognition_task = None

        # Check if recognizer is available
        if not self.recognizer:
            raise RuntimeError("Speech recognizer not available")

        if not self.recognizer.isAvailable():
            raise RuntimeError("Speech recognition not available on this device")

        logger.info(f"Wake word detector initialized (wake word: '{wake_word}')")
        logger.info(f"Speech recognizer locale: {self.recognizer.locale()}")

    def start_listening(self, callback: Callable[[], None]):
        """Start continuous wake word detection.

        Args:
            callback: Function to call when wake word is detected
        """
        if self._is_listening:
            logger.warning("Already listening for wake word")
            return

        self._callback = callback
        self._is_listening = True
        self._stop_event.clear()

        # Start listening thread
        self._listen_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True,
        )
        self._listen_thread.start()
        logger.info("Started listening for wake word")

    def _listen_loop(self):
        """Continuous wake word detection loop using Apple Speech framework."""
        logger.info("Wake word detection loop started")

        try:
            # Configure audio session
            audio_session = AVAudioSession.sharedInstance()
            error = None

            success = audio_session.setCategory_mode_options_error_(
                AVAudioSessionCategoryRecord,
                AVAudioSessionModeDefault,
                0,
                None
            )

            if not success[0]:
                logger.error(f"Failed to set audio session category: {success[1]}")
                return

            success = audio_session.setActive_error_(True, None)
            if not success[0]:
                logger.error(f"Failed to activate audio session: {success[1]}")
                return

            # Get the input node
            input_node = self.audio_engine.inputNode()
            if not input_node:
                logger.error("No audio input node available")
                return

            # Get the recording format
            recording_format = input_node.outputFormatForBus_(0)

            logger.info(f"Audio format: {recording_format.sampleRate()} Hz, {recording_format.channelCount()} channels")

            # Create recognition request
            self.recognition_request = SFSpeechAudioBufferRecognitionRequest.alloc().init()
            if not self.recognition_request:
                logger.error("Unable to create recognition request")
                return

            self.recognition_request.setShouldReportPartialResults_(True)

            # Install tap on input node to capture audio
            def audio_tap_block(buffer, when):
                """Callback for audio buffer."""
                if self.recognition_request:
                    self.recognition_request.appendAudioPCMBuffer_(buffer)

            input_node.installTapOnBus_bufferSize_format_block_(
                0,  # bus
                1024,  # buffer size
                recording_format,
                audio_tap_block
            )

            # Start audio engine
            self.audio_engine.prepare()
            success = self.audio_engine.startAndReturnError_(None)
            if not success[0]:
                logger.error(f"Audio engine failed to start: {success[1]}")
                return

            logger.info("Audio engine started, listening for wake word...")

            # Start recognition task
            def recognition_handler(result, error):
                """Handle recognition results."""
                if error:
                    logger.error(f"Recognition error: {error}")
                    return

                if result:
                    transcription = result.bestTranscription().formattedString().lower()

                    # Log partial results for debugging
                    if result.isFinal():
                        logger.debug(f"Final transcription: {transcription}")
                    else:
                        logger.debug(f"Partial transcription: {transcription}")

                    # Check if wake word is in the transcription
                    if self.wake_word in transcription:
                        logger.info(f"Wake word '{self.wake_word}' detected in: '{transcription}'")

                        # Call the callback
                        if self._callback:
                            try:
                                self._callback()
                            except Exception as e:
                                logger.error(f"Error in wake word callback: {e}", exc_info=True)

                        # Reset recognition to continue listening
                        # (We'll restart it after a short delay to avoid duplicate detections)
                        time.sleep(2)

            self.recognition_task = self.recognizer.recognitionTaskWithRequest_resultHandler_(
                self.recognition_request,
                recognition_handler
            )

            # Keep the thread alive while listening
            while not self._stop_event.is_set():
                time.sleep(0.1)

        except Exception as e:
            logger.error(f"Error in wake word detection loop: {e}", exc_info=True)

        finally:
            # Clean up
            self._cleanup()
            logger.info("Wake word detection loop stopped")

    def _cleanup(self):
        """Clean up audio engine and recognition resources."""
        try:
            # Stop recognition task
            if self.recognition_task:
                self.recognition_task.cancel()
                self.recognition_task = None

            # Stop audio engine
            if self.audio_engine:
                input_node = self.audio_engine.inputNode()
                if input_node:
                    input_node.removeTapOnBus_(0)

                if self.audio_engine.isRunning():
                    self.audio_engine.stop()

            # End recognition request
            if self.recognition_request:
                self.recognition_request.endAudio()
                self.recognition_request = None

            # Deactivate audio session
            audio_session = AVAudioSession.sharedInstance()
            audio_session.setActive_error_(False, None)

            logger.debug("Audio resources cleaned up")

        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)

    def stop_listening(self):
        """Stop wake word detection."""
        if not self._is_listening:
            return

        logger.info("Stopping wake word detection...")
        self._stop_event.set()
        self._is_listening = False

        if self._listen_thread:
            self._listen_thread.join(timeout=2.0)
            self._listen_thread = None

        logger.info("Stopped listening for wake word")

    def is_listening(self) -> bool:
        """Check if currently listening for wake word.

        Returns:
            True if listening, False otherwise
        """
        return self._is_listening


# Singleton instance
_detector: Optional[WakeWordDetector] = None


def get_detector(wake_word: str = "chandler") -> WakeWordDetector:
    """Get or create wake word detector singleton.

    Args:
        wake_word: The wake word to detect

    Returns:
        WakeWordDetector instance
    """
    global _detector
    if _detector is None:
        _detector = WakeWordDetector(wake_word)
    return _detector


def start_listening(callback: Callable[[], None], wake_word: str = "chandler"):
    """Convenience function to start wake word detection.

    Args:
        callback: Function to call when wake word is detected
        wake_word: The wake word to detect
    """
    detector = get_detector(wake_word)
    detector.start_listening(callback)


def stop_listening():
    """Convenience function to stop wake word detection."""
    global _detector
    if _detector:
        _detector.stop_listening()


def request_permissions() -> bool:
    """Request microphone and speech recognition permissions.

    Returns:
        True if permissions granted, False otherwise
    """
    if not SPEECH_AVAILABLE:
        logger.error("Speech framework not available")
        return False

    logger.info("Requesting speech recognition permission...")

    # Request speech recognition permission
    permission_granted = [False]
    permission_checked = threading.Event()

    def permission_handler(status):
        """Handle permission response."""
        from Speech import (
            SFSpeechRecognizerAuthorizationStatusAuthorized,
            SFSpeechRecognizerAuthorizationStatusDenied,
            SFSpeechRecognizerAuthorizationStatusRestricted,
            SFSpeechRecognizerAuthorizationStatusNotDetermined,
        )

        if status == SFSpeechRecognizerAuthorizationStatusAuthorized:
            logger.info("Speech recognition permission granted")
            permission_granted[0] = True
        elif status == SFSpeechRecognizerAuthorizationStatusDenied:
            logger.error("Speech recognition permission denied")
        elif status == SFSpeechRecognizerAuthorizationStatusRestricted:
            logger.error("Speech recognition restricted on this device")
        else:
            logger.warning("Speech recognition permission not determined")

        permission_checked.set()

    # Request authorization
    SFSpeechRecognizer.requestAuthorization_(permission_handler)

    # Wait for permission response (with timeout)
    permission_checked.wait(timeout=5.0)

    return permission_granted[0]
