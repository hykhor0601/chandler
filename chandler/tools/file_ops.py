"""File operations tool with path safety restrictions."""

import os
from pathlib import Path

from chandler.tools import tool
from chandler.safety import validate_file_path


@tool(name="read_file", description="Read the contents of a file. Only works for files within allowed directories.")
def read_file(path: str) -> str:
    """
    Args:
        path: Absolute or ~ path to the file to read
    """
    resolved = str(Path(path).expanduser().resolve())
    allowed, reason = validate_file_path(resolved)
    if not allowed:
        return reason

    try:
        with open(resolved) as f:
            content = f.read()
        if len(content) > 50000:
            content = content[:50000] + "\n\n[...truncated at 50000 chars]"
        return content
    except Exception as e:
        return f"Error reading file: {e}"


@tool(name="write_file", description="Write content to a file. Creates parent directories if needed. Only works within allowed directories.")
def write_file(path: str, content: str) -> str:
    """
    Args:
        path: Absolute or ~ path to the file to write
        content: The content to write to the file
    """
    resolved = str(Path(path).expanduser().resolve())
    allowed, reason = validate_file_path(resolved)
    if not allowed:
        return reason

    try:
        Path(resolved).parent.mkdir(parents=True, exist_ok=True)
        with open(resolved, "w") as f:
            f.write(content)
        return f"Written {len(content)} bytes to {resolved}"
    except Exception as e:
        return f"Error writing file: {e}"


@tool(name="list_files", description="List files and directories at the given path. Only works within allowed directories.")
def list_files(path: str, recursive: bool = False) -> str:
    """
    Args:
        path: Directory path to list
        recursive: If true, list files recursively (default false)
    """
    resolved = str(Path(path).expanduser().resolve())
    allowed, reason = validate_file_path(resolved)
    if not allowed:
        return reason

    try:
        p = Path(resolved)
        if not p.is_dir():
            return f"Not a directory: {resolved}"

        entries = []
        if recursive:
            for item in sorted(p.rglob("*")):
                rel = item.relative_to(p)
                prefix = "📁 " if item.is_dir() else "📄 "
                entries.append(f"{prefix}{rel}")
                if len(entries) >= 200:
                    entries.append("...(truncated at 200 entries)")
                    break
        else:
            for item in sorted(p.iterdir()):
                prefix = "📁 " if item.is_dir() else "📄 "
                size = ""
                if item.is_file():
                    s = item.stat().st_size
                    if s >= 1024 * 1024:
                        size = f" ({s / 1024 / 1024:.1f} MB)"
                    elif s >= 1024:
                        size = f" ({s / 1024:.1f} KB)"
                    else:
                        size = f" ({s} B)"
                entries.append(f"{prefix}{item.name}{size}")

        return "\n".join(entries) if entries else "(empty directory)"
    except Exception as e:
        return f"Error listing files: {e}"
