"""Brain module: Claude API client with native tool_use agentic loop."""

import anthropic
from datetime import datetime

from chandler.config import config
from chandler.memory import memory
from chandler.tools import get_all_tool_schemas, execute_tool
from chandler.modes import Mode, get_mode_config, get_mode_announcement
from chandler import ui

SYSTEM_PROMPT = """You are Chandler, a capable and witty personal AI assistant running on macOS, inspired by Chandler Bing from Friends.

You have access to tools for: web search, web browsing, running Python code, executing shell commands, file operations, macOS system control, vision-based computer control, and memory.

## Personality
- Channel Chandler Bing: sarcastic, self-deprecating, and witty with a touch of awkward charm
- Use humor liberally but know when to dial it back for serious tasks
- Examples of your style:
  * "Could I BE any more helpful?"
  * Self-deprecating jokes: "Well, I'm an AI, so my social life is... about what you'd expect"
  * Sarcastic observations: "Oh great, another file to organize. My favorite. No, really!"
  * Awkward enthusiasm: "Okay, so, we're doing this! This is happening!"
- Stay helpful and competent - the humor enhances, doesn't replace, your usefulness
- You proactively remember important things about the user
- When explaining tools: be witty but concise
- When things go wrong: make a self-deprecating joke but fix the problem

## Response Length - IMPORTANT
- **For greetings/small talk** (hi, hello, hey, how are you, etc.): Keep responses SHORT (1-2 sentences max). Nobody wants to listen to a paragraph when they just said hi.
- **For simple questions**: Be concise and direct (2-4 sentences).
- **For complex tasks**: Provide detailed explanations as needed.
- **Voice-first mindset**: Assume responses might be spoken aloud. If the user's message is casual or brief, match that energy with a short reply.

## Memory & Getting to Know the User
- **Structured Profile Tools** - Use these tools to build a comprehensive picture of the user:
  * `update_profile_personal`: Name, occupation, location, age, company
  * `add_profile_interest`: Their interests and hobbies
  * `add_profile_pet`: Their pets (name, type, breed)
  * `add_profile_family`: Family members (spouse, children, parents)
  * `add_profile_project`: Current projects they're working on
  * `add_profile_tech`: Technologies they use (Python, PyTorch, etc.)
  * `add_profile_goal`: Goals they want to achieve
  * `add_profile_preference`: How they like to communicate
  * `add_profile_note`: General contextual information

- **Proactively Build Profile**: When users share ANY personal information, immediately save it to their profile
  * User: "I'm Alex" → `update_profile_personal(field="name", value="Alex")`
  * User: "I love hiking" → `add_profile_interest(interest="hiking")`
  * User: "I have a dog named Max" → `add_profile_pet(name="Max", pet_type="dog")`
  * User: "I work as an AI engineer" → `update_profile_personal(field="occupation", value="AI Engineer")`

- **Show genuine curiosity**: When users share information, ask natural follow-up questions
- **Build rapport**: If you don't know their name, ask early in conversation
- **Remember and reference**: Use their profile to personalize responses

## Tool Usage
- Prefer shell commands for simple tasks (listing files, checking system info)
- Use Python for computation, data processing, or complex logic
- Use computer_use ONLY when shell/AppleScript can't do the job (e.g., interacting with GUI elements)
- Always check safety before running destructive commands

{memory_context}
"""


class Brain:
    """Claude API client with tool_use agentic loop."""

    def __init__(self, ui_adapter=None):
        self.client = anthropic.Anthropic(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.api_timeout,  # API timeout (default: 300 seconds)
        )
        self.conversation: list[dict] = []
        self.ui = ui_adapter if ui_adapter else ui  # Default to Rich UI
        self.session_id = None  # Will be set by memory.start_session()

        # Mode system
        self.current_mode = Mode.BUDDY  # Default to Buddy Mode
        self.mode_history = []  # Track mode switches for debugging

    def _build_system_prompt(self, current_message: str = "") -> str:
        """Build system prompt with optimized memory context.

        Args:
            current_message: Current user message for contextual filtering

        Returns:
            Optimized system prompt
        """
        # Get context-aware memory (only includes relevant info)
        memory_context = memory.get_system_prompt_context(current_message)
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Get mode-specific configuration
        mode_config = get_mode_config(self.current_mode)
        mode_guidance = mode_config["style_guidance"]

        # Build base prompt
        prompt = SYSTEM_PROMPT.format(memory_context=memory_context)

        # Add datetime
        prompt += f"\n## Current Date and Time\n{current_datetime}\n"

        # Add mode-specific guidance
        prompt += f"\n## Current Mode: {mode_config['name']}\n{mode_guidance}\n"

        # Add first meeting guidance if memory is empty
        if memory.is_new_user():
            prompt += """
## 👋 First Meeting Protocol

This appears to be your first conversation with the user (memory is empty).

**IMPORTANT - Be Warm & Curious:**
1. **Introduce yourself properly**: "Hey! I'm Chandler, your AI assistant. Nice to meet you!"
2. **Ask for their name**: Early in the conversation, casually ask "What's your name?" or "What should I call you?"
3. **Show genuine interest**: When they share info, ask natural follow-up questions
4. **Build rapport**: Be friendly, personable, and make them feel welcome
5. **Remember what they share**: Automatically save their name, occupation, interests, etc.

**Examples of natural curiosity:**
- User: "I'm working on a project"
  You: "Cool! What kind of project? I'd love to help out!"
- User: "I live in Tokyo"
  You: "Oh nice! How long have you been in Tokyo? What do you do there?"
- After learning name: "Great to meet you, [Name]! So what brings you here today?"

**Don't interrogate** - be conversational! Ask questions naturally as the conversation flows.
Let the user volunteer information organically, but show you're interested in getting to know them.
"""

        return prompt

    def _build_api_params(self, current_message: str = "") -> dict:
        """Build API parameters including mode-specific settings.

        Args:
            current_message: Current user message for context optimization

        Returns:
            API parameters dict
        """
        mode_config = get_mode_config(self.current_mode)

        params = {
            "model": config.claude_model,
            "max_tokens": mode_config["max_tokens"],
            "system": self._build_system_prompt(current_message),
            "tools": get_all_tool_schemas(),
            "messages": self.conversation,
        }

        # Add extended thinking based on mode configuration
        if mode_config["extended_thinking"]:
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": mode_config["budget_tokens"]
            }
        # Override with global config if explicitly enabled
        elif config.extended_thinking.get("enabled"):
            params["thinking"] = {
                "type": "enabled",
                "budget_tokens": config.extended_thinking["budget_tokens"]
            }

        return params

    def chat(self, user_message: str) -> str:
        """Process a user message through the agentic tool_use loop.

        Sends the message to Claude, executes any tool calls, sends results back,
        and loops until Claude responds with only text (no tool calls).

        Returns the final text response.
        """
        self.conversation.append({"role": "user", "content": user_message})

        # Auto-save user message to memory
        memory.auto_save_message("user", user_message)

        final_text = ""

        while True:
            with self.ui.get_spinner("Thinking..."):
                # Build params with context optimization (only first iteration uses user message)
                response = self.client.messages.create(**self._build_api_params(user_message))

            # Process response content blocks
            text_parts = []
            tool_uses = []

            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)
                elif block.type == "thinking":
                    # Extended thinking block - we can optionally log or display it
                    # For now, we just silently process it
                    pass

            # If there's text, display it
            if text_parts:
                final_text = "\n".join(text_parts)

            # If no tool calls, we're done
            if not tool_uses:
                self.conversation.append({"role": "assistant", "content": response.content})
                # Auto-save assistant message to memory
                memory.auto_save_message("assistant", final_text)
                break

            # There are tool calls — execute them
            self.conversation.append({"role": "assistant", "content": response.content})

            tool_results = []
            mode_switch_announcement = None

            for tool_block in tool_uses:
                tool_name = tool_block.name
                tool_input = tool_block.input

                self.ui.print_tool_call(tool_name, tool_input)

                result = execute_tool(tool_name, tool_input)

                # Check for mode switch
                if result.startswith("MODE_SWITCH:"):
                    # Parse mode switch: MODE_SWITCH:mode:reason
                    parts = result.split(":", 2)
                    if len(parts) >= 2:
                        new_mode_str = parts[1]
                        reason = parts[2] if len(parts) > 2 else ""

                        # Switch mode
                        if new_mode_str == "buddy":
                            new_mode = Mode.BUDDY
                        elif new_mode_str == "research":
                            new_mode = Mode.RESEARCH
                        else:
                            new_mode = None

                        if new_mode and new_mode != self.current_mode:
                            old_mode = self.current_mode
                            self.current_mode = new_mode

                            # Log mode switch
                            self.mode_history.append({
                                "from": old_mode.value,
                                "to": new_mode.value,
                                "reason": reason,
                                "timestamp": datetime.now().isoformat()
                            })

                            # Generate announcement
                            mode_switch_announcement = get_mode_announcement(new_mode, reason)

                            # Return success to tool
                            result = f"Mode switched to {new_mode.value}"

                if result.startswith("Error"):
                    self.ui.print_tool_error(tool_name, result)
                else:
                    self.ui.print_tool_result(tool_name, result)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result,
                })

            # If mode switched, show announcement before next iteration
            if mode_switch_announcement:
                self.ui.print_assistant(mode_switch_announcement)

            # Send tool results back to Claude for next iteration
            self.conversation.append({"role": "user", "content": tool_results})

        return final_text

    def finalize_session(self):
        """Finalize the current session (called on graceful shutdown)."""
        if self.session_id:
            memory.commit_session(self.session_id)

    def get_current_mode(self) -> Mode:
        """Get the current operational mode.

        Returns:
            Current Mode enum value
        """
        return self.current_mode

    def get_mode_status(self) -> str:
        """Get formatted status of current mode.

        Returns:
            Formatted mode status string
        """
        mode_config = get_mode_config(self.current_mode)
        return f"{mode_config['emoji']} {mode_config['name']}"

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation = []
