"""Mode control tool - allows Chandler to switch between operational modes."""

from chandler.tools import tool
from chandler.modes import Mode


@tool(
    name="switch_mode",
    description="Switch Chandler's operational mode between Buddy and Research modes"
)
def switch_mode(mode: str, reason: str = "") -> str:
    """Switch Chandler's operational mode.

    Use this tool when you need to change your operational style:
    - Switch to "research" when user asks deep, complex questions requiring thorough analysis
    - Switch to "buddy" when returning to casual conversation or research is complete

    Args:
        mode: Target mode - either "buddy" or "research"
        reason: Brief explanation for why you're switching (helps with debugging)

    Returns:
        Confirmation message

    Examples:
        switch_mode(mode="research", reason="User asked about transformer attention theory")
        switch_mode(mode="buddy", reason="Research question answered, user said thanks")
    """
    mode = mode.lower().strip()

    if mode not in ["buddy", "research"]:
        return f"Error: Invalid mode '{mode}'. Use 'buddy' or 'research'."

    # Note: The actual mode switch is handled by Brain
    # This tool just signals the intent - Brain will process it
    return f"MODE_SWITCH:{mode}:{reason}"
