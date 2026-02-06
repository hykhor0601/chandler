"""Memory tools for Claude to save and recall information about the user."""

from chandler.tools import tool
from chandler.memory import memory


@tool(name="remember", description="Save a fact or piece of information about the user for future reference. Use this proactively when you learn something important about the user (name, preferences, background, etc.).")
def remember(key: str, value: str) -> str:
    """
    Args:
        key: A short descriptive key for this memory (e.g. 'name', 'favorite_language', 'current_project')
        value: The information to remember
    """
    return memory.remember(key, value)


@tool(name="recall", description="Search your memory for previously saved information about the user. Use this when you need to recall something you learned in a previous conversation.")
def recall(query: str) -> str:
    """
    Args:
        query: Search query to find relevant memories (e.g. 'name', 'project', 'preferences')
    """
    return memory.recall(query)
