"""Safety layer: command validation, path restrictions, user confirmation."""

import re
from pathlib import Path

from chandler.config import config

# Dangerous command patterns (shell)
_DANGEROUS_PATTERNS = [
    r"\brm\s+(-\w*\s+)*-\w*r\w*f\b.*\s+/\s*$",  # rm -rf /
    r"\brm\s+(-\w*\s+)*-\w*r\w*f\b.*\s+/\s",     # rm -rf / ...
    r"\bmkfs\b",
    r"\bdd\b\s+.*\bof=/dev/",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",   # fork bomb
    r"\b(shutdown|reboot|halt|poweroff)\b",
    r"\bchmod\s+(-\w+\s+)*777\s+/",
    r"\bchown\s+.*\s+/",
    r"\bcurl\b.*\|\s*(ba)?sh",                      # curl | sh
    r"\bwget\b.*\|\s*(ba)?sh",
]

_DANGEROUS_COMPILED = [re.compile(p) for p in _DANGEROUS_PATTERNS]

# Commands that are destructive but can be allowed with confirmation
_CONFIRM_PATTERNS = [
    r"\brm\b",
    r"\bmv\b.*\s+/",
    r"\bkill\b",
    r"\bpkill\b",
    r"\bkillall\b",
    r"\bsudo\b",
    r"\bchmod\b",
    r"\bchown\b",
    r"\bgit\s+(push|reset|clean|checkout\s+--)\b",
    r"\bpip\s+uninstall\b",
    r"\bbrew\s+(uninstall|remove)\b",
]

_CONFIRM_COMPILED = [re.compile(p) for p in _CONFIRM_PATTERNS]


def is_dangerous_command(command: str) -> bool:
    """Check if a shell command is in the blocklist (never allowed)."""
    for pattern in _DANGEROUS_COMPILED:
        if pattern.search(command):
            return True
    return False


def needs_confirmation(command: str) -> bool:
    """Check if a shell command needs user confirmation before execution."""
    if not config.safety.get("require_confirmation_for_destructive", True):
        return False
    for pattern in _CONFIRM_COMPILED:
        if pattern.search(command):
            return True
    return False


def is_path_allowed(path: str) -> bool:
    """Check if a file path is within allowed directories."""
    try:
        resolved = str(Path(path).expanduser().resolve())
        for allowed in config.allowed_directories:
            if resolved.startswith(allowed):
                return True
        return False
    except (ValueError, OSError):
        return False


def confirm_action(description: str) -> bool:
    """Ask user for confirmation of a potentially dangerous action."""
    try:
        response = input(f"\n⚠️  {description}\nProceed? [y/N]: ").strip().lower()
        return response in ("y", "yes")
    except (EOFError, KeyboardInterrupt):
        return False


def validate_shell_command(command: str) -> tuple[bool, str]:
    """Validate a shell command. Returns (allowed, reason)."""
    if is_dangerous_command(command):
        return False, f"Blocked: dangerous command detected in '{command}'"

    if needs_confirmation(command):
        if not confirm_action(f"Execute potentially destructive command: {command}"):
            return False, "User declined to execute command."

    return True, "OK"


def validate_file_path(path: str) -> tuple[bool, str]:
    """Validate a file path against allowed directories."""
    if not is_path_allowed(path):
        return False, f"Access denied: '{path}' is outside allowed directories"
    return True, "OK"
