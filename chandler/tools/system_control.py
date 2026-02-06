"""macOS system control via osascript and open commands."""

import subprocess

from chandler.tools import tool


@tool(name="system_control", description="Control macOS using AppleScript (osascript) or system commands. Can open apps, control windows, adjust volume, show notifications, etc.")
def system_control(action: str, target: str = "") -> str:
    """
    Args:
        action: The action to perform: 'open_app', 'open_url', 'notification', 'volume', 'brightness', 'say', 'applescript'
        target: The target/argument for the action (app name, URL, notification text, volume level 0-100, or raw AppleScript)
    """
    try:
        if action == "open_app":
            result = subprocess.run(
                ["open", "-a", target],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                return f"Opened {target}"
            return f"Failed to open {target}: {result.stderr}"

        elif action == "open_url":
            result = subprocess.run(
                ["open", target],
                capture_output=True, text=True, timeout=10,
            )
            return f"Opened {target}" if result.returncode == 0 else f"Failed: {result.stderr}"

        elif action == "notification":
            script = f'display notification "{target}" with title "Chandler"'
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=10,
            )
            return f"Notification sent: {target}"

        elif action == "volume":
            level = int(target)
            script = f"set volume output volume {level}"
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True, text=True, timeout=10,
            )
            return f"Volume set to {level}"

        elif action == "say":
            subprocess.run(
                ["say", target],
                capture_output=True, text=True, timeout=30,
            )
            return f"Said: {target}"

        elif action == "applescript":
            result = subprocess.run(
                ["osascript", "-e", target],
                capture_output=True, text=True, timeout=30,
            )
            output = result.stdout.strip()
            if result.returncode != 0:
                return f"AppleScript error: {result.stderr}"
            return output or "AppleScript executed."

        else:
            return f"Unknown action: {action}. Available: open_app, open_url, notification, volume, say, applescript"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out"
    except Exception as e:
        return f"Error: {e}"
