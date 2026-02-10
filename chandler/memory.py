"""Persistent memory system for Chandler.

Stores user profile, facts, and conversation summaries in a JSON file.
Auto-saves conversation sessions to prevent data loss.
"""

import json
import threading
import queue
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from chandler.config import config
from chandler.user_profile import UserProfile

logger = logging.getLogger(__name__)


class FactExtractionWorker(threading.Thread):
    """Background worker for extracting facts from conversations."""

    def __init__(self):
        super().__init__(daemon=True)
        self.queue: queue.Queue = queue.Queue()
        self._stop_event = threading.Event()
        self._memory_ref: Optional['Memory'] = None

    def set_memory(self, memory: 'Memory'):
        """Set memory reference for accessing data."""
        self._memory_ref = memory

    def stop(self):
        """Stop the worker thread."""
        self._stop_event.set()

    def schedule_extraction(self, messages: List[Dict[str, Any]]):
        """Schedule fact extraction from recent messages.

        Args:
            messages: List of message dicts with 'role' and 'content'
        """
        if not self._memory_ref:
            logger.warning("FactExtractionWorker: No memory reference set")
            return

        self.queue.put(messages)
        logger.info(f"Scheduled fact extraction for {len(messages)} messages")

    def run(self):
        """Worker loop - processes extraction jobs."""
        logger.info("FactExtractionWorker started")

        while not self._stop_event.is_set():
            try:
                # Wait for job with timeout to check stop_event
                messages = self.queue.get(timeout=1)
            except queue.Empty:
                continue

            try:
                self._extract_facts(messages)
            except Exception as e:
                logger.error(f"Fact extraction failed: {e}", exc_info=True)
            finally:
                self.queue.task_done()

        logger.info("FactExtractionWorker stopped")

    def _extract_facts(self, messages: List[Dict[str, Any]]):
        """Extract facts from messages using Claude API.

        Args:
            messages: List of message dicts to analyze
        """
        if not self._memory_ref:
            return

        try:
            # Import here to avoid circular dependency
            import anthropic

            # Build extraction prompt
            conversation_text = "\n\n".join([
                f"{msg['role']}: {msg['content']}"
                for msg in messages
                if isinstance(msg['content'], str)
            ])

            extraction_prompt = f"""Analyze this conversation and extract key facts about the user.

Conversation:
{conversation_text}

Extract only explicit facts mentioned by the user (not assumptions or inferences). Format as JSON:
{{
    "user_profile": {{"key": "value"}},  // Personal info (name, location, occupation, etc.)
    "facts": {{"key": "value"}}  // Other memorable facts
}}

Only include facts that are clearly stated. If no facts found, return empty objects."""

            client = anthropic.Anthropic(
                api_key=config.api_key,
                base_url=config.base_url,
                timeout=60,
            )

            response = client.messages.create(
                model=config.claude_model,
                max_tokens=1024,
                messages=[{"role": "user", "content": extraction_prompt}],
            )

            # Parse response
            response_text = response.content[0].text if response.content else ""
            logger.debug(f"Fact extraction response: {response_text}")

            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                extracted = json.loads(json_match.group())

                # Merge extracted facts into memory
                for key, value in extracted.get("user_profile", {}).items():
                    self._memory_ref.remember(key, value)

                for key, value in extracted.get("facts", {}).items():
                    self._memory_ref.remember(key, value)

                logger.info(f"Extracted and saved {len(extracted.get('user_profile', {}))} profile items and {len(extracted.get('facts', {}))} facts")
            else:
                logger.warning("No JSON found in fact extraction response")

        except Exception as e:
            logger.error(f"Error in _extract_facts: {e}", exc_info=True)


class Memory:
    """Persistent memory backed by a JSON file with automatic session saving."""

    def __init__(self):
        self._path = config.data_dir / "memory.json"
        self._data = self._load()

        # Session management
        self._conversations_dir = config.data_dir / "conversations"
        self._temp_dir = config.data_dir / "temp"
        self._current_session_path: Optional[Path] = None
        self._current_session_messages: List[Dict[str, Any]] = []
        self._message_count = 0

        # Create directories
        self._conversations_dir.mkdir(parents=True, exist_ok=True)
        self._temp_dir.mkdir(parents=True, exist_ok=True)

        # Background fact extraction worker
        self.fact_worker = FactExtractionWorker()
        self.fact_worker.set_memory(self)
        self.fact_worker.start()

        # User profile system
        self.user_profile = UserProfile(config.data_dir / "user_profile.json")

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

    def is_new_user(self) -> bool:
        """Check if this is a new user (no stored memories).

        Returns:
            True if memory is empty (new user), False otherwise
        """
        # Check both old memory and new profile system
        profile = self._data.get("user_profile", {})
        facts = self._data.get("facts", {})
        summaries = self._data.get("conversation_summaries", [])

        return not profile and not facts and not summaries and self.user_profile.is_empty()

    def get_system_prompt_context(self, current_message: str = "") -> str:
        """Generate optimized memory context for system prompt.

        Uses tiered approach to minimize token usage:
        - Always: Core identity (name, occupation)
        - Often: Top interests, active projects, tech stack
        - On-demand: Pets, family, goals (only when relevant to conversation)

        Args:
            current_message: Current user message for context relevance detection

        Returns:
            Concise, relevant memory context
        """
        parts = []

        # TIER 1 & 2: Core profile summary (optimized, max 5 lines)
        profile_summary = self.user_profile.get_system_prompt_summary(max_lines=5)
        if profile_summary:
            parts.append("## User Profile:")
            parts.append(profile_summary)

        # TIER 3: Contextual info (only if relevant to current message)
        if current_message:
            contextual_info = self.user_profile.get_contextual_info(current_message.lower())
            if contextual_info:
                parts.append("\n## Relevant Context:")
                parts.append(contextual_info)

        # Legacy facts (only if not redundant with profile)
        facts = self._data.get("facts", {})
        # Filter out facts that are already in profile
        if facts:
            # Keep only first 3 facts for efficiency
            fact_items = list(facts.items())[:3]
            if fact_items:
                parts.append("\n## Additional Notes:")
                for k, v in fact_items:
                    parts.append(f"- {k}: {v}")

        # Recent conversation summaries (max 2 for efficiency)
        summaries = self._data.get("conversation_summaries", [])
        if summaries:
            recent = summaries[-2:]  # Only last 2 sessions
            if recent:
                parts.append(f"\n## Recent Context ({len(summaries)} past sessions):")
                for s in recent:
                    # Truncate to 100 chars for efficiency
                    parts.append(f"- [{s.get('date', '?')[:10]}] {s.get('summary', '')[:100]}")

        return "\n".join(parts) if parts else "No memories yet — this is a new user."

    def start_session(self) -> str:
        """Start a new conversation session.

        Returns:
            Session ID (timestamp-based)
        """
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_session_path = self._temp_dir / "current_session.json"
        self._current_session_messages = []
        self._message_count = 0

        logger.info(f"Started new session: {session_id}")
        return session_id

    def auto_save_message(self, role: str, content: str):
        """Auto-save a message to the current session.

        Args:
            role: "user" or "assistant"
            content: Message text
        """
        if self._current_session_path is None:
            # Auto-start session if not started
            self.start_session()

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }

        self._current_session_messages.append(message)
        self._message_count += 1

        # Save to temp file immediately (crash recovery)
        try:
            with open(self._current_session_path, "w") as f:
                json.dump({
                    "messages": self._current_session_messages,
                    "message_count": self._message_count,
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to auto-save message: {e}")

        # Schedule fact extraction every 5 messages
        if self._message_count % 5 == 0 and self._message_count > 0:
            # Get last 5 messages for fact extraction
            recent_messages = self._current_session_messages[-5:]
            self.fact_worker.schedule_extraction(recent_messages)

    def commit_session(self, session_id: Optional[str] = None):
        """Commit the current session to permanent storage.

        Args:
            session_id: Optional session ID (will generate if not provided)
        """
        if not self._current_session_messages:
            logger.info("No messages to commit")
            return

        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save to permanent conversations directory
        permanent_path = self._conversations_dir / f"session_{session_id}.json"

        try:
            with open(permanent_path, "w") as f:
                json.dump({
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "message_count": self._message_count,
                    "messages": self._current_session_messages,
                }, f, indent=2, ensure_ascii=False)

            logger.info(f"Session committed: {permanent_path}")

            # Remove temp file
            if self._current_session_path and self._current_session_path.exists():
                self._current_session_path.unlink()

            # Reset session state
            self._current_session_path = None
            self._current_session_messages = []
            self._message_count = 0

        except Exception as e:
            logger.error(f"Failed to commit session: {e}", exc_info=True)

    def cleanup_old_sessions(self, days: int = 30):
        """Delete session files older than specified days.

        Args:
            days: Number of days to keep sessions
        """
        cutoff = datetime.now().timestamp() - (days * 86400)

        for session_file in self._conversations_dir.glob("session_*.json"):
            if session_file.stat().st_mtime < cutoff:
                try:
                    session_file.unlink()
                    logger.info(f"Deleted old session: {session_file.name}")
                except Exception as e:
                    logger.error(f"Failed to delete {session_file.name}: {e}")


# Singleton
memory = Memory()
