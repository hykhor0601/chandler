"""User profile management tools.

Allows Chandler to build and maintain a comprehensive picture of the user.
"""

from chandler.tools import tool
from chandler.memory import memory


@tool(
    name="update_profile_personal",
    description="Update user's personal information (name, age, location, occupation, company, etc.)"
)
def update_profile_personal(field: str, value: str) -> str:
    """Update a personal info field in user's profile.

    Args:
        field: Field name (name, age, location, occupation, company, title, etc.)
        value: Field value

    Returns:
        Confirmation message

    Examples:
        update_profile_personal(field="name", value="Alice")
        update_profile_personal(field="occupation", value="AI Engineer")
        update_profile_personal(field="location", value="Tokyo")
    """
    memory.user_profile.update_personal(field, value)
    return f"Updated {field}: {value}"


@tool(
    name="add_profile_interest",
    description="Add an interest or hobby to user's profile"
)
def add_profile_interest(interest: str) -> str:
    """Add an interest or hobby.

    Args:
        interest: The interest/hobby (e.g., "machine learning", "hiking", "photography")

    Returns:
        Confirmation message
    """
    memory.user_profile.add_interest(interest)
    return f"Added interest: {interest}"


@tool(
    name="add_profile_pet",
    description="Add information about user's pet"
)
def add_profile_pet(name: str, pet_type: str, breed: str = "", notes: str = "") -> str:
    """Add a pet to user's profile.

    Args:
        name: Pet's name
        pet_type: Type of pet (dog, cat, bird, fish, etc.)
        breed: Breed (optional)
        notes: Additional notes about the pet (optional)

    Returns:
        Confirmation message

    Examples:
        add_profile_pet(name="Max", pet_type="dog", breed="Golden Retriever")
        add_profile_pet(name="Whiskers", pet_type="cat", notes="Loves to sleep")
    """
    memory.user_profile.add_pet(name, pet_type, breed, notes)
    return f"Added pet: {name} ({pet_type})"


@tool(
    name="add_profile_family",
    description="Add information about user's family member"
)
def add_profile_family(relation: str, name: str) -> str:
    """Add a family member to user's profile.

    Args:
        relation: Relationship (spouse, partner, child, parent, sibling, etc.)
        name: Person's name

    Returns:
        Confirmation message

    Examples:
        add_profile_family(relation="spouse", name="Jordan")
        add_profile_family(relation="child", name="Emma")
    """
    memory.user_profile.update_family(relation, name)
    return f"Added family: {relation} - {name}"


@tool(
    name="add_profile_project",
    description="Add a project user is working on"
)
def add_profile_project(name: str, description: str = "", status: str = "active") -> str:
    """Add a project to user's profile.

    Args:
        name: Project name
        description: Project description (optional)
        status: Project status - "active", "completed", or "paused" (default: active)

    Returns:
        Confirmation message

    Examples:
        add_profile_project(name="RAG system", description="Building RAG for customer support")
        add_profile_project(name="ML pipeline", status="active")
    """
    memory.user_profile.add_project(name, description, status)
    return f"Added project: {name} ({status})"


@tool(
    name="update_profile_preference",
    description="Update user's communication or interaction preferences"
)
def update_profile_preference(preference: str, value: str) -> str:
    """Update a user preference.

    Args:
        preference: Preference key (communication_style, response_length, technical_level, etc.)
        value: Preference value

    Returns:
        Confirmation message

    Examples:
        update_profile_preference(preference="communication_style", value="direct")
        update_profile_preference(preference="response_length", value="concise")
        update_profile_preference(preference="technical_level", value="expert")
    """
    memory.user_profile.update_preference(preference, value)
    return f"Updated preference: {preference} = {value}"


@tool(
    name="add_profile_goal",
    description="Add a goal user wants to achieve"
)
def add_profile_goal(goal: str) -> str:
    """Add a goal to user's profile.

    Args:
        goal: The goal description

    Returns:
        Confirmation message

    Examples:
        add_profile_goal(goal="Learn about transformer architecture")
        add_profile_goal(goal="Build production ML system")
    """
    memory.user_profile.add_goal(goal)
    return f"Added goal: {goal}"


@tool(
    name="add_profile_tech",
    description="Add a technology/tool to user's tech stack"
)
def add_profile_tech(technology: str) -> str:
    """Add a technology to user's tech stack.

    Args:
        technology: Technology name (Python, PyTorch, React, Docker, etc.)

    Returns:
        Confirmation message

    Examples:
        add_profile_tech(technology="PyTorch")
        add_profile_tech(technology="Docker")
    """
    memory.user_profile.add_tech(technology)
    return f"Added to tech stack: {technology}"


@tool(
    name="add_profile_note",
    description="Add a contextual note about the user (general information that doesn't fit other categories)"
)
def add_profile_note(note: str) -> str:
    """Add a contextual note to user's profile.

    Args:
        note: The note text

    Returns:
        Confirmation message

    Examples:
        add_profile_note(note="Working on RAG project for company")
        add_profile_note(note="Prefers morning meetings")
    """
    memory.user_profile.add_note(note)
    return f"Added note: {note}"
