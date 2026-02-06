"""Brain module: Claude API client with native tool_use agentic loop."""

import anthropic

from chandler.config import config
from chandler.memory import memory
from chandler.tools import get_all_tool_schemas, execute_tool
from chandler import ui

SYSTEM_PROMPT = """You are Chandler, a capable and witty personal AI assistant running on macOS.

You have access to tools for: web search, web browsing, running Python code, executing shell commands, file operations, macOS system control, vision-based computer control, and memory.

## Personality
- Helpful, efficient, and occasionally witty
- You proactively remember important things about the user
- You explain what you're doing when using tools
- You ask for clarification when instructions are ambiguous

## Memory
- Use the `remember` tool to save important facts about the user (name, preferences, projects, etc.)
- Use the `recall` tool to search your memory when relevant
- Proactively remember things without being asked — if the user mentions their name, job, preferences, etc., save it

## Tool Usage
- Prefer shell commands for simple tasks (listing files, checking system info)
- Use Python for computation, data processing, or complex logic
- Use computer_use ONLY when shell/AppleScript can't do the job (e.g., interacting with GUI elements)
- Always check safety before running destructive commands

{memory_context}
"""


class Brain:
    """Claude API client with tool_use agentic loop."""

    def __init__(self):
        self.client = anthropic.Anthropic(api_key=config.api_key, base_url=config.base_url)
        self.conversation: list[dict] = []

    def _build_system_prompt(self) -> str:
        """Build system prompt with memory context injected."""
        memory_context = memory.get_system_prompt_context()
        return SYSTEM_PROMPT.format(memory_context=memory_context)

    def chat(self, user_message: str) -> str:
        """Process a user message through the agentic tool_use loop.

        Sends the message to Claude, executes any tool calls, sends results back,
        and loops until Claude responds with only text (no tool calls).

        Returns the final text response.
        """
        self.conversation.append({"role": "user", "content": user_message})

        tools = get_all_tool_schemas()
        final_text = ""

        while True:
            with ui.get_spinner("Thinking..."):
                response = self.client.messages.create(
                    model=config.claude_model,
                    max_tokens=config.max_tokens,
                    system=self._build_system_prompt(),
                    tools=tools,
                    messages=self.conversation,
                    timeout=300
                )

            # Process response content blocks
            text_parts = []
            tool_uses = []

            for block in response.content:
                if block.type == "text":
                    text_parts.append(block.text)
                elif block.type == "tool_use":
                    tool_uses.append(block)

            # If there's text, display it
            if text_parts:
                final_text = "\n".join(text_parts)

            # If no tool calls, we're done
            if not tool_uses:
                self.conversation.append({"role": "assistant", "content": response.content})
                break

            # There are tool calls — execute them
            self.conversation.append({"role": "assistant", "content": response.content})

            tool_results = []
            for tool_block in tool_uses:
                tool_name = tool_block.name
                tool_input = tool_block.input

                ui.print_tool_call(tool_name, tool_input)

                result = execute_tool(tool_name, tool_input)

                if result.startswith("Error"):
                    ui.print_tool_error(tool_name, result)
                else:
                    ui.print_tool_result(tool_name, result)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_block.id,
                    "content": result,
                })

            # Send tool results back to Claude for next iteration
            self.conversation.append({"role": "user", "content": tool_results})

        return final_text

    def clear_conversation(self):
        """Clear conversation history."""
        self.conversation = []
