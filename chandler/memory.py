"""Persistent memory system for Chandler.

Stores user profile, facts, and conversation summaries in a JSON file.
"""

import json
from pathlib import Path
from datetime import datetime

from chandler.config import config


class Memory:
    """Persistent memory backed by a JSON file."""

    def __init__(self):
        self._path = config.data_dir / "memory.json"
        self._data = self._load()

    def _load(self) -> dict:
        """Load memory from disk."""
        if self._path.exists():
            try:
                with open(self._path) as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                pass
        return {"user_profile": {}, "facts": {}, "conversation_summaries": []}

    def _save(self):
        """Persist memory to disk."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with open(self._path, "w") as f:
            json.dump(self._data, f, indent=2, ensure_ascii=False)

    @property
    def user_profile(self) -> dict:
        return self._data.get("user_profile", {})

    @property
    def facts(self) -> dict:
        return self._data.get("facts", {})

    @property
    def conversation_summaries(self) -> list:
        return self._data.get("conversation_summaries", [])

    @property
    def all_data(self) -> dict:
        return self._data

    def remember(self, key: str, value: str) -> str:
        """Store a fact or user info.

        If key starts with 'user_' or is a profile field (name, age, location, etc.),
        it goes into user_profile. Otherwise into facts.
        """
        profile_keys = {
            "name", "age", "location", "occupation", "job", "email",
            "language", "preferences", "background", "interests", "hobbies",
        }

        clean_key = key.lower().replace("user_", "")
        if clean_key in profile_keys or key.startswith("user_"):
            self._data["user_profile"][clean_key] = value
        else:
            self._data["facts"][key] = value

        self._save()
        return f"Remembered: {key} = {value}"

    def recall(self, query: str) -> str:
        """Search memory for relevant facts."""
        results = []
        query_lower = query.lower()

        # Search user profile
        for k, v in self._data.get("user_profile", {}).items():
            if query_lower in k.lower() or query_lower in str(v).lower():
                results.append(f"[profile] {k}: {v}")

        # Search facts
        for k, v in self._data.get("facts", {}).items():
            if query_lower in k.lower() or query_lower in str(v).lower():
                results.append(f"[fact] {k}: {v}")

        # Search conversation summaries
        for summary in self._data.get("conversation_summaries", []):
            text = summary.get("summary", "")
            if query_lower in text.lower():
                date = summary.get("date", "unknown")
                results.append(f"[conversation {date}] {text[:200]}")

        if not results:
            return "No matching memories found."
        return "\n".join(results)

    def add_conversation_summary(self, summary: str):
        """Add a summary of a conversation session."""
        max_summaries = config.memory_settings.get("max_conversation_summaries", 50)
        self._data.setdefault("conversation_summaries", []).append({
            "date": datetime.now().isoformat(),
            "summary": summary,
        })
        # Keep only the most recent summaries
        if len(self._data["conversation_summaries"]) > max_summaries:
            self._data["conversation_summaries"] = self._data["conversation_summaries"][-max_summaries:]
        self._save()

    def get_system_prompt_context(self) -> str:
        """Generate memory context string for injection into system prompt."""
        parts = []

        profile = self._data.get("user_profile", {})
        if profile:
            parts.append("## What you know about the user:")
            for k, v in profile.items():
                parts.append(f"- {k}: {v}")

        facts = self._data.get("facts", {})
        if facts:
            parts.append("\n## Remembered facts:")
            for k, v in facts.items():
                parts.append(f"- {k}: {v}")

        summaries = self._data.get("conversation_summaries", [])
        if summaries:
            parts.append(f"\n## Past conversations: {len(summaries)} sessions")
            for s in summaries[-3:]:
                parts.append(f"- [{s.get('date', '?')}] {s.get('summary', '')[:150]}")

        return "\n".join(parts) if parts else "No memories yet — this is a new user."


# Singleton
memory = Memory()
