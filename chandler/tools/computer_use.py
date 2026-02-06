"""Computer use tool: vision-based GUI automation."""

from chandler.tools import tool
from chandler.config import config


@tool(name="computer_use", description="Control the computer using vision-based GUI automation. Takes a screenshot, analyzes it with AI, and performs mouse/keyboard actions to accomplish the objective. Use this only when shell commands or AppleScript cannot accomplish the task.")
def computer_use(objective: str) -> str:
    """
    Args:
        objective: Natural language description of what to do on screen (e.g. 'Open Safari and navigate to google.com', 'Click the submit button')
    """
    # Check if user confirmation is required
    if config.safety.get("require_confirmation_for_computer_control", True):
        from chandler.safety import confirm_action
        if not confirm_action(f"Computer control: {objective}"):
            return "User declined computer control action."

    # Check if vision model is configured
    vm = config.vision_model
    if not vm.get("api_key"):
        return "Error: Vision model API key not configured. Set vision_model.api_key in config.yaml or ~/.chandler/config.yaml"

    try:
        from chandler.computer_control import ComputerController
        controller = ComputerController()
        return controller.run(objective)
    except Exception as e:
        return f"Computer control error: {e}"
