"""Execute Python code in a sandboxed subprocess."""

import subprocess
import tempfile
import os

from chandler.tools import tool


@tool(name="run_python", description="Execute Python code and return the output. Code runs in a separate subprocess with a 30-second timeout.")
def run_python(code: str) -> str:
    """
    Args:
        code: Python code to execute
    """
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write(code)
            tmp_path = f.name

        try:
            result = subprocess.run(
                ["python3", tmp_path],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += ("\n--- stderr ---\n" + result.stderr) if output else result.stderr
            if result.returncode != 0:
                output += f"\n[exit code: {result.returncode}]"
            return output or "(no output)"
        finally:
            os.unlink(tmp_path)
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out (30s limit)"
    except Exception as e:
        return f"Error running Python code: {e}"
