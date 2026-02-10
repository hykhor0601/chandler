"""Configuration loader for Chandler."""

import os
from pathlib import Path
from typing import Any

import yaml

# Default config path: next to this file
_DEFAULT_CONFIG = Path(__file__).parent / "config.yaml"
# User config: ~/.chandler/config.yaml
_USER_CONFIG = Path.home() / ".chandler" / "config.yaml"

_DEFAULTS = {
    "anthropic_api_key": "",
    "anthropic_base_url": "https://api.anthropic.com",
    "vision_model": {
        "api_key": "",
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-4o",
    },
    "claude_model": "claude-sonnet-4-20250514",
    "max_tokens": 4096,
    "allowed_directories": ["~"],
    "safety": {
        "require_confirmation_for_destructive": True,
        "require_confirmation_for_computer_control": True,
    },
    "computer_control": {
        "max_iterations": 15,
        "timeout": 180,
        "screenshot_max_size": 1280,
        "active_window_only": False,
    },
    "memory": {
        "max_conversation_summaries": 50,
    },
}


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge override into base dict."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class Config:
    """Application configuration loaded from YAML with environment overrides."""

    def __init__(self):
        self._data: dict[str, Any] = _DEFAULTS.copy()
        self._load()

    def _load(self):
        # Load bundled default config
        if _DEFAULT_CONFIG.exists():
            with open(_DEFAULT_CONFIG) as f:
                bundled = yaml.safe_load(f) or {}
            self._data = _deep_merge(self._data, bundled)

        # Load user config (overrides bundled)
        if _USER_CONFIG.exists():
            with open(_USER_CONFIG) as f:
                user = yaml.safe_load(f) or {}
            self._data = _deep_merge(self._data, user)

        # Environment variable overrides
        env_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if env_key:
            self._data["anthropic_api_key"] = env_key

    @property
    def api_key(self) -> str:
        return self._data.get("anthropic_api_key", "")

    @property
    def base_url(self) -> str:
        return self._data.get("anthropic_base_url", "https://api.anthropic.com")

    @property
    def claude_model(self) -> str:
        return self._data.get("claude_model", "claude-sonnet-4-20250514")

    @property
    def max_tokens(self) -> int:
        return self._data.get("max_tokens", 4096)

    @property
    def api_timeout(self) -> float:
        return self._data.get("api_timeout", 300.0)

    @property
    def vision_model(self) -> dict:
        return self._data.get("vision_model", _DEFAULTS["vision_model"])

    @property
    def allowed_directories(self) -> list[str]:
        dirs = self._data.get("allowed_directories", ["~"])
        return [str(Path(d).expanduser().resolve()) for d in dirs]

    @property
    def safety(self) -> dict:
        return self._data.get("safety", _DEFAULTS["safety"])

    @property
    def computer_control(self) -> dict:
        return self._data.get("computer_control", _DEFAULTS["computer_control"])

    @property
    def memory_settings(self) -> dict:
        return self._data.get("memory", _DEFAULTS["memory"])

    @property
    def extended_thinking(self) -> dict:
        return self._data.get("extended_thinking", {
            "enabled": False,
            "budget_tokens": 10000,
            "min_budget": 1024,
            "max_budget": 64000,
        })

    @property
    def voice_mode(self) -> dict:
        return self._data.get("voice_mode", {
            "enabled": True,
            "wake_word": "chandler",
            "wake_word_contains": True,
            "wake_word_asr": {
                "provider": "apple_speech",
                "confidence_threshold": 0.7,
            },
            "high_precision_asr": {
                "provider": "user_stub",
                "timeout": 30,
                "silence_threshold": 2.0,
            },
            "tts": {
                "voice": "Samantha",
                "rate": 200,
                "use_built_in": True,
            },
            "menu_bar": {
                "auto_open_on_wake": True,
                "show_error_notifications": True,
                "show_listening_notifications": False,
                "conversation_history_limit": 50,
            },
        })

    @property
    def data_dir(self) -> Path:
        return Path(__file__).parent / "data"

    def save_api_key(self, key: str):
        """Save API key to user config."""
        _USER_CONFIG.parent.mkdir(parents=True, exist_ok=True)
        user_data = {}
        if _USER_CONFIG.exists():
            with open(_USER_CONFIG) as f:
                user_data = yaml.safe_load(f) or {}
        user_data["anthropic_api_key"] = key
        with open(_USER_CONFIG, "w") as f:
            yaml.dump(user_data, f, default_flow_style=False)
        self._data["anthropic_api_key"] = key


# Singleton
config = Config()
