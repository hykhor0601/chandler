"""Rich terminal UI for Chandler."""

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.syntax import Syntax
from rich.spinner import Spinner
from rich.live import Live
from rich.text import Text

console = Console()


def print_welcome():
    """Print the welcome banner."""
    console.print(
        Panel(
            "[bold cyan]Chandler[/bold cyan] — Personal AI Assistant\n"
            "[dim]Type your message, or use /help for commands[/dim]",
            border_style="cyan",
            padding=(1, 2),
        )
    )


def print_assistant(text: str):
    """Print assistant response as rendered markdown."""
    console.print()
    console.print(Markdown(text))
    console.print()


def print_streaming_text(text: str):
    """Print text without newline for streaming output."""
    console.print(text, end="")


def print_tool_call(tool_name: str, args: dict):
    """Display a tool being called."""
    args_str = ", ".join(f"{k}={repr(v)[:60]}" for k, v in args.items())
    console.print(f"  [dim]⚙ {tool_name}({args_str})[/dim]")


def print_tool_result(tool_name: str, result: str, max_len: int = 500):
    """Display a tool result."""
    display = result[:max_len] + "..." if len(result) > max_len else result
    console.print(f"  [dim green]✓ {tool_name} → {display}[/dim green]")


def print_tool_error(tool_name: str, error: str):
    """Display a tool error."""
    console.print(f"  [bold red]✗ {tool_name} → {error}[/bold red]")


def print_error(message: str):
    """Print an error message."""
    console.print(f"[bold red]Error:[/bold red] {message}")


def print_info(message: str):
    """Print an info message."""
    console.print(f"[cyan]{message}[/cyan]")


def print_warning(message: str):
    """Print a warning message."""
    console.print(f"[yellow]⚠ {message}[/yellow]")


def print_memory(memory_data: dict):
    """Display memory contents in a formatted panel."""
    lines = []
    profile = memory_data.get("user_profile", {})
    if profile:
        lines.append("[bold]User Profile:[/bold]")
        for k, v in profile.items():
            lines.append(f"  {k}: {v}")
        lines.append("")

    facts = memory_data.get("facts", {})
    if facts:
        lines.append("[bold]Remembered Facts:[/bold]")
        for k, v in facts.items():
            lines.append(f"  {k}: {v}")
        lines.append("")

    summaries = memory_data.get("conversation_summaries", [])
    if summaries:
        lines.append(f"[bold]Conversation Summaries:[/bold] {len(summaries)} stored")

    if not lines:
        lines.append("[dim]No memories stored yet.[/dim]")

    console.print(Panel("\n".join(lines), title="Memory", border_style="magenta"))


def print_help():
    """Print available commands."""
    console.print(
        Panel(
            "[bold]/help[/bold]    — Show this help\n"
            "[bold]/memory[/bold]  — Show stored memories\n"
            "[bold]/clear[/bold]   — Clear conversation history\n"
            "[bold]/quit[/bold]    — Exit Chandler",
            title="Commands",
            border_style="blue",
        )
    )


def get_spinner(message: str = "Thinking...") -> Live:
    """Create a spinner context for long operations."""
    return Live(
        Spinner("dots", text=f"[cyan]{message}[/cyan]"),
        console=console,
        transient=True,
    )


def get_user_input() -> str:
    """Get input from user with styled prompt."""
    try:
        return console.input("[bold green]You:[/bold green] ")
    except (EOFError, KeyboardInterrupt):
        return "/quit"
