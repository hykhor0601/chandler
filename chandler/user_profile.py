"""User Profile System - Maintains a comprehensive picture of the user.

Organizes user information into structured categories:
- Personal info (name, age, location, occupation)
- Interests & hobbies
- Pets
- Family
- Current projects
- Preferences (communication style, technical level)
- Goals
- Tech stack
- Important notes
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class UserProfile:
    """Manages a structured, comprehensive user profile."""

    def __init__(self, profile_path: Path):
        """Initialize user profile.

        Args:
            profile_path: Path to profile JSON file
        """
        self._path = profile_path
        self._data = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load profile from disk."""
        if self._path.exists():
            try:
                with open(self._path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass

        # Default profile structure
        return {
            "personal": {},
            "interests": [],
            "pets": [],
            "family": {},
            "projects": [],
            "preferences": {},
            "goals": [],
            "tech_stack": [],
            "important_dates": {},
            "notes": [],
            "last_updated": None,
        }

    def _save(self):
        """Save profile to disk."""
        self._data["last_updated"] = datetime.now().isoformat()
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    # Personal Info
    def update_personal(self, field: str, value: str):
        """Update a personal info field.

        Args:
            field: Field name (name, age, location, occupation, company, etc.)
            value: Field value
        """
        self._data["personal"][field] = value
        self._save()

    def get_personal(self, field: str) -> Optional[str]:
        """Get a personal info field."""
        return self._data["personal"].get(field)

    # Interests
    def add_interest(self, interest: str):
        """Add an interest or hobby."""
        if interest not in self._data["interests"]:
            self._data["interests"].append(interest)
            self._save()

    def remove_interest(self, interest: str):
        """Remove an interest."""
        if interest in self._data["interests"]:
            self._data["interests"].remove(interest)
            self._save()

    # Pets
    def add_pet(self, name: str, pet_type: str, breed: str = "", notes: str = ""):
        """Add a pet.

        Args:
            name: Pet's name
            pet_type: Type (dog, cat, bird, etc.)
            breed: Breed (optional)
            notes: Additional notes
        """
        pet = {
            "name": name,
            "type": pet_type,
            "breed": breed,
            "notes": notes,
        }
        self._data["pets"].append(pet)
        self._save()

    def remove_pet(self, name: str):
        """Remove a pet by name."""
        self._data["pets"] = [p for p in self._data["pets"] if p["name"] != name]
        self._save()

    # Family
    def update_family(self, relation: str, name: str):
        """Update family member.

        Args:
            relation: Relationship (spouse, partner, child, parent, sibling, etc.)
            name: Person's name
        """
        self._data["family"][relation] = name
        self._save()

    # Projects
    def add_project(self, name: str, description: str = "", status: str = "active"):
        """Add a project.

        Args:
            name: Project name
            description: Project description
            status: Project status (active, completed, paused)
        """
        project = {
            "name": name,
            "description": description,
            "status": status,
            "added": datetime.now().isoformat(),
        }
        self._data["projects"].append(project)
        self._save()

    def update_project_status(self, name: str, status: str):
        """Update project status."""
        for project in self._data["projects"]:
            if project["name"] == name:
                project["status"] = status
                self._save()
                break

    def remove_project(self, name: str):
        """Remove a project."""
        self._data["projects"] = [p for p in self._data["projects"] if p["name"] != name]
        self._save()

    # Preferences
    def update_preference(self, key: str, value: str):
        """Update a preference.

        Args:
            key: Preference key (communication_style, response_length, technical_level, etc.)
            value: Preference value
        """
        self._data["preferences"][key] = value
        self._save()

    # Goals
    def add_goal(self, goal: str):
        """Add a goal."""
        if goal not in self._data["goals"]:
            self._data["goals"].append(goal)
            self._save()

    def remove_goal(self, goal: str):
        """Remove a goal."""
        if goal in self._data["goals"]:
            self._data["goals"].remove(goal)
            self._save()

    # Tech Stack
    def add_tech(self, technology: str):
        """Add a technology to tech stack."""
        if technology not in self._data["tech_stack"]:
            self._data["tech_stack"].append(technology)
            self._save()

    def remove_tech(self, technology: str):
        """Remove a technology from tech stack."""
        if technology in self._data["tech_stack"]:
            self._data["tech_stack"].remove(technology)
            self._save()

    # Important Dates
    def add_date(self, event: str, date: str):
        """Add an important date.

        Args:
            event: Event name (birthday, anniversary, etc.)
            date: Date in ISO format (YYYY-MM-DD)
        """
        self._data["important_dates"][event] = date
        self._save()

    # Notes
    def add_note(self, note: str):
        """Add a contextual note."""
        note_entry = {
            "date": datetime.now().isoformat(),
            "note": note,
        }
        self._data["notes"].append(note_entry)
        # Keep only last 50 notes
        if len(self._data["notes"]) > 50:
            self._data["notes"] = self._data["notes"][-50:]
        self._save()

    # Query & Display
    def get_full_profile(self) -> Dict[str, Any]:
        """Get the complete profile."""
        return self._data

    def get_summary(self) -> str:
        """Get a formatted summary of the profile."""
        lines = []

        # Personal
        personal = self._data["personal"]
        if personal:
            lines.append("## Personal Info")
            for key, value in personal.items():
                lines.append(f"- {key.title()}: {value}")
            lines.append("")

        # Interests
        interests = self._data["interests"]
        if interests:
            lines.append("## Interests & Hobbies")
            for interest in interests:
                lines.append(f"- {interest}")
            lines.append("")

        # Pets
        pets = self._data["pets"]
        if pets:
            lines.append("## Pets")
            for pet in pets:
                pet_str = f"- {pet['name']} ({pet['type']}"
                if pet.get("breed"):
                    pet_str += f", {pet['breed']}"
                pet_str += ")"
                if pet.get("notes"):
                    pet_str += f" - {pet['notes']}"
                lines.append(pet_str)
            lines.append("")

        # Family
        family = self._data["family"]
        if family:
            lines.append("## Family")
            for relation, name in family.items():
                lines.append(f"- {relation.title()}: {name}")
            lines.append("")

        # Projects
        projects = self._data["projects"]
        if projects:
            lines.append("## Current Projects")
            for project in projects:
                status_emoji = "🟢" if project["status"] == "active" else "⏸️" if project["status"] == "paused" else "✅"
                lines.append(f"- {status_emoji} {project['name']}")
                if project.get("description"):
                    lines.append(f"  {project['description']}")
            lines.append("")

        # Preferences
        preferences = self._data["preferences"]
        if preferences:
            lines.append("## Preferences")
            for key, value in preferences.items():
                lines.append(f"- {key.replace('_', ' ').title()}: {value}")
            lines.append("")

        # Goals
        goals = self._data["goals"]
        if goals:
            lines.append("## Goals")
            for goal in goals:
                lines.append(f"- {goal}")
            lines.append("")

        # Tech Stack
        tech_stack = self._data["tech_stack"]
        if tech_stack:
            lines.append("## Tech Stack")
            lines.append(f"- {', '.join(tech_stack)}")
            lines.append("")

        # Important Dates
        important_dates = self._data["important_dates"]
        if important_dates:
            lines.append("## Important Dates")
            for event, date in important_dates.items():
                lines.append(f"- {event.title()}: {date}")
            lines.append("")

        # Recent Notes
        notes = self._data["notes"]
        if notes:
            lines.append("## Recent Notes")
            for note in notes[-5:]:  # Show last 5
                date = note["date"][:10]  # Just the date
                lines.append(f"- [{date}] {note['note']}")
            lines.append("")

        if not lines:
            return "No profile information yet. Tell me about yourself!"

        return "\n".join(lines)

    def is_empty(self) -> bool:
        """Check if profile is empty."""
        return (
            not self._data["personal"]
            and not self._data["interests"]
            and not self._data["pets"]
            and not self._data["family"]
            and not self._data["projects"]
            and not self._data["goals"]
        )

    def get_system_prompt_summary(self, max_lines: int = 5, include_context_hints: bool = True) -> str:
        """Get a concise, optimized summary for system prompt injection.

        Uses tiered approach to minimize token usage while maintaining relevance.

        Args:
            max_lines: Maximum lines to include (default: 5 for token efficiency)
            include_context_hints: Include hints for accessing more detail

        Returns:
            Concise summary string
        """
        lines = []

        # TIER 1: Core Identity (Always include)
        name = self.get_personal("name")
        occupation = self.get_personal("occupation")

        if name and occupation:
            lines.append(f"User: {name}, {occupation}")
        elif name:
            lines.append(f"User: {name}")
        elif occupation:
            lines.append(f"User's occupation: {occupation}")

        # TIER 2: Frequently Relevant (Compact format)
        # Top 3 interests only
        interests = self._data["interests"][:3]
        if interests:
            lines.append(f"Interests: {', '.join(interests)}")

        # Active projects (max 2)
        active_projects = [p["name"] for p in self._data["projects"] if p["status"] == "active"][:2]
        if active_projects:
            lines.append(f"Working on: {', '.join(active_projects)}")

        # Tech stack (top 3 only)
        tech = self._data["tech_stack"][:3]
        if tech:
            lines.append(f"Uses: {', '.join(tech)}")

        # Limit to max_lines for efficiency
        lines = lines[:max_lines]

        # Add context hint if there's more data
        if include_context_hints and self._has_additional_context():
            lines.append("(More profile details available via profile tools)")

        return "\n".join(lines) if lines else ""

    def _has_additional_context(self) -> bool:
        """Check if there's additional context not shown in summary."""
        return (
            len(self._data["interests"]) > 3
            or len(self._data["pets"]) > 0
            or len(self._data["family"]) > 0
            or len(self._data["goals"]) > 0
            or len(self._data["preferences"]) > 0
        )

    def get_contextual_info(self, query_lower: str) -> str:
        """Get relevant profile info based on conversation context.

        This is called ON-DEMAND when certain keywords are detected.

        Args:
            query_lower: User's message in lowercase for keyword detection

        Returns:
            Relevant profile information, or empty string if not relevant
        """
        relevant_info = []

        # Pet-related keywords
        if any(word in query_lower for word in ["pet", "dog", "cat", "animal", "puppy", "kitten"]):
            pets = self._data["pets"]
            if pets:
                pet_list = [f"{p['name']} ({p['type']}" + (f", {p['breed']}" if p.get('breed') else "") + ")"
                           for p in pets]
                relevant_info.append(f"Pets: {', '.join(pet_list)}")

        # Family-related keywords
        if any(word in query_lower for word in ["family", "spouse", "wife", "husband", "child", "parent", "sibling"]):
            family = self._data["family"]
            if family:
                family_list = [f"{relation}: {name}" for relation, name in family.items()]
                relevant_info.append(f"Family: {', '.join(family_list)}")

        # Goal-related keywords
        if any(word in query_lower for word in ["goal", "learn", "achieve", "want to", "planning"]):
            goals = self._data["goals"]
            if goals:
                relevant_info.append(f"Goals: {', '.join(goals[:3])}")

        # Preference-related keywords
        if any(word in query_lower for word in ["prefer", "like", "style", "way"]):
            prefs = self._data["preferences"]
            if prefs:
                pref_list = [f"{k.replace('_', ' ')}: {v}" for k, v in prefs.items()]
                relevant_info.append(f"Preferences: {', '.join(pref_list)}")

        return "\n".join(relevant_info) if relevant_info else ""
