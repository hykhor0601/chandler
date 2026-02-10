"""Text-to-speech interface for Chandler voice mode.

USER: Replace this stub with your preferred TTS implementation!
Default: Uses macOS built-in 'say' command.
"""

import subprocess
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def speak(text: str, voice: Optional[str] = None, rate: Optional[int] = None):
    """Speak text using text-to-speech.

    Default implementation uses macOS built-in 'say' command.

    USER: Replace with your preferred TTS implementation!

    Example implementations:

    1. OpenAI TTS API:
    ```python
    import openai
    from playsound import playsound

    def speak(text, voice=None, rate=None):
        response = openai.Audio.create_speech(
            model="tts-1",
            voice=voice or "alloy",
            input=text,
        )
        response.stream_to_file("/tmp/speech.mp3")
        playsound("/tmp/speech.mp3")
    ```

    2. ElevenLabs API:
    ```python
    from elevenlabs import generate, play

    def speak(text, voice=None, rate=None):
        audio = generate(
            text=text,
            voice=voice or "Bella",
            model="eleven_monolingual_v1"
        )
        play(audio)
    ```

    3. Azure Speech:
    ```python
    import azure.cognitiveservices.speech as speechsdk

    def speak(text, voice=None, rate=None):
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_KEY,
            region=AZURE_REGION
        )
        speech_config.speech_synthesis_voice_name = voice or "en-US-JennyNeural"
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        synthesizer.speak_text_async(text).get()
    ```

    Args:
        text: Text to speak
        voice: Voice name (default: system default or "Samantha" for macOS)
        rate: Speech rate in words per minute (default: system default or 200)
    """
    if not text or not text.strip():
        logger.warning("Empty text provided to TTS")
        return

    logger.info(f"Speaking text: '{text[:50]}...'")

    try:
        # Use macOS built-in 'say' command
        cmd = ["say"]

        # Add voice if specified
        if voice:
            cmd.extend(["-v", voice])

        # Add rate if specified
        if rate:
            cmd.extend(["-r", str(rate)])

        # Add text
        cmd.append(text)

        # Execute command
        subprocess.run(cmd, check=True)
        logger.info("TTS completed successfully")

    except subprocess.CalledProcessError as e:
        logger.error(f"TTS failed: {e}")
    except FileNotFoundError:
        logger.error("'say' command not found - TTS not available on this system")


def list_voices() -> list[str]:
    """List available TTS voices.

    Returns:
        List of voice names
    """
    try:
        # List macOS voices
        result = subprocess.run(
            ["say", "-v", "?"],
            capture_output=True,
            text=True,
            check=True,
        )

        voices = []
        for line in result.stdout.strip().split("\n"):
            # Parse voice name from output
            # Format: "Voice_Name    language_code    # Description"
            parts = line.split()
            if parts:
                voices.append(parts[0])

        return voices

    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("Could not list voices")
        return []


def test_tts() -> bool:
    """Test if TTS is working.

    Returns:
        True if TTS works, False otherwise
    """
    try:
        subprocess.run(
            ["say", "Testing text to speech"],
            check=True,
            timeout=5,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        return False


# TTS configuration presets
TTS_CONFIGS = {
    "macos_default": {
        "voice": "Samantha",
        "rate": 200,
    },
    "macos_fast": {
        "voice": "Samantha",
        "rate": 250,
    },
    "macos_slow": {
        "voice": "Samantha",
        "rate": 150,
    },
    "macos_alex": {
        "voice": "Alex",
        "rate": 200,
    },
}


def speak_with_config(text: str, config_name: str = "macos_default"):
    """Speak text using a preset configuration.

    Args:
        text: Text to speak
        config_name: Configuration preset name
    """
    config = TTS_CONFIGS.get(config_name, TTS_CONFIGS["macos_default"])
    speak(text, voice=config["voice"], rate=config["rate"])
