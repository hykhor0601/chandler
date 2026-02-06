"""Execute shell commands with safety checks."""

import subprocess

from chandler.tools import tool
from chandler.safety import validate_shell_command


@tool(name="run_shell", description="Execute a shell command on macOS and return its output. Commands are validated for safety before execution.")
def run_shell(command: str) -> str:
    """
    Args:
        command: The shell command to execute
    """
    allowed, reason = validate_shell_command(command)
    if not allowed:
        return reason

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = ""
        if result.stdout:
            output += result.stdout
        if result.stderr:
            output += ("\n--- stderr ---\n" + result.stderr) if output else result.stderr
        if result.returncode != 0 and not output:
            output = f"Command failed with exit code {result.returncode}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out (60s limit)"
    except Exception as e:
        return f"Error executing command: {e}"
