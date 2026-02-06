"""Vision-based computer controller adapted from vision-controller.

Captures screenshots, sends to a vision LLM for analysis, and executes
mouse/keyboard actions based on the LLM's instructions.
"""

import base64
import json
import os
import platform
import re
import tempfile
import time

import cv2
import numpy as np
import pyautogui
import pyperclip

from chandler.config import config

# macOS window management
if platform.system() == "Darwin":
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID,
    )
    from AppKit import NSWorkspace

# Safety: disable PyAutoGUI failsafe by default (we have our own safety)
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

SYSTEM_PROMPT = """You are a computer vision assistant that controls a macOS desktop.
You will receive a screenshot of the current screen and an objective to accomplish.

Respond with a JSON object containing:
{
  "status": "in_progress" | "completed" | "failed",
  "description": "Brief description of what you see and your plan",
  "action": {
    "type": "click" | "double_click" | "right_click" | "drag" | "scroll_up" | "scroll_down" | "hotkey" | "input" | "wait",
    "coordinates": [x, y],  // coordinates in 0-1000 scale (relative to image)
    "text": ""  // text to type (for input action) or hotkey combo (for hotkey action)
  }
}

Rules:
- Coordinates use a 0-1000 scale where (0,0) is top-left and (1000,1000) is bottom-right
- For drag: coordinates should be [[startX, startY], [endX, endY]]
- For hotkey: text should be space-separated keys like "command c" or "command shift s"
- For input: click the target field first, then type text
- Set status to "completed" when the objective is achieved
- Set status to "failed" if the objective cannot be achieved
- Only output valid JSON, no other text
"""


class ComputerController:
    """Vision-based GUI automation controller."""

    def __init__(self):
        cc_config = config.computer_control
        vm_config = config.vision_model

        self.max_iterations = cc_config.get("max_iterations", 15)
        self.timeout = cc_config.get("timeout", 180)
        self.max_screenshot_size = cc_config.get("screenshot_max_size", 1280)
        self.active_window_only = cc_config.get("active_window_only", False)

        self.api_key = vm_config.get("api_key", "")
        self.base_url = vm_config.get("base_url", "https://api.openai.com/v1")
        self.model_name = vm_config.get("model_name", "gpt-4o")

        self._screenshot_dir = tempfile.mkdtemp(prefix="chandler_")
        self._screenshot_path = os.path.join(self._screenshot_dir, "screen.png")
        self._history = []
        self._should_exit = False

    def _get_active_window_bounds(self):
        """Get active window bounds on macOS."""
        try:
            workspace = NSWorkspace.sharedWorkspace()
            active_app = workspace.frontmostApplication()
            if not active_app:
                return None

            window_list = CGWindowListCopyWindowInfo(
                kCGWindowListOptionOnScreenOnly, kCGNullWindowID
            )
            for window in window_list:
                if (window.get("kCGWindowOwnerName") == active_app.localizedName()
                        and window.get("kCGWindowLayer", 999) == 0):
                    bounds = window.get("kCGWindowBounds", {})
                    x, y = int(bounds.get("X", 0)), int(bounds.get("Y", 0))
                    w, h = int(bounds.get("Width", 0)), int(bounds.get("Height", 0))
                    if w > 0 and h > 0:
                        return (x, y, w, h)
        except Exception:
            pass
        return None

    def _capture_screen(self):
        """Capture screenshot and return (scale_factor, window_offset)."""
        window_offset = {"x": 0, "y": 0}

        if self.active_window_only:
            bounds = self._get_active_window_bounds()
            if bounds:
                x, y, w, h = bounds
                window_offset = {"x": x, "y": y}
                screenshot = pyautogui.screenshot(region=(x, y, w, h))
            else:
                screenshot = pyautogui.screenshot()
        else:
            screenshot = pyautogui.screenshot()

        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        # Resize if needed
        scale = 1.0
        h, w = img.shape[:2]
        max_edge = max(h, w)
        if max_edge > self.max_screenshot_size:
            scale = self.max_screenshot_size / max_edge
            img = cv2.resize(img, None, fx=scale, fy=scale)

        cv2.imwrite(self._screenshot_path, img, [int(cv2.IMWRITE_PNG_COMPRESSION), 1])
        return scale, window_offset

    def _get_screenshot_base64(self):
        """Read screenshot and return base64 string."""
        with open(self._screenshot_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")

    def _call_vision_llm(self, objective):
        """Send screenshot + objective to vision LLM and get response."""
        from openai import OpenAI

        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        screenshot_b64 = self._get_screenshot_base64()

        # Build message
        if self._history:
            user_text = f"Continue the task: {objective}. Here is the current screen:"
        else:
            user_text = objective

        user_message = {
            "role": "user",
            "content": [
                {"type": "text", "text": user_text},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_b64}"}},
            ],
        }
        self._history.append(user_message)

        # Build messages list with image management
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        recent = self._history[-5:]
        for i, msg in enumerate(recent):
            if i < len(recent) - 2 and isinstance(msg.get("content"), list):
                # Remove images from older messages
                cleaned = {"role": msg["role"], "content": [
                    p for p in msg["content"] if p.get("type") != "image_url"
                ]}
                messages.append(cleaned)
            else:
                messages.append(msg)

        response = client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=1000,
            temperature=0.1,
        )

        ai_text = response.choices[0].message.content
        self._history.append({"role": "assistant", "content": ai_text})
        return ai_text

    def _parse_response(self, text):
        """Parse JSON response from vision LLM."""
        # Try to extract JSON from code blocks
        if "```" in text:
            match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
            if match:
                text = match.group(1)
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            return {"status": "failed", "description": "Failed to parse response", "action": {"type": "wait"}}

    def _map_coordinates(self, x, y, scale, img_width, img_height, window_offset):
        """Map coordinates from model space (0-1000) to screen space."""
        # Read image dimensions
        img = cv2.imread(self._screenshot_path)
        if img is not None:
            img_height, img_width = img.shape[:2]

        x_abs = (x / 1000) * img_width
        y_abs = (y / 1000) * img_height

        # Apply scale
        x_screen = x_abs / scale
        y_screen = y_abs / scale

        # Apply window offset
        x_screen += window_offset.get("x", 0)
        y_screen += window_offset.get("y", 0)

        return max(0, x_screen), max(0, y_screen)

    def _execute_action(self, action, scale, window_offset):
        """Execute a parsed action dict."""
        action_type = action.get("type", "wait")
        coordinates = action.get("coordinates", [])
        text = action.get("text", "")

        if action_type == "wait":
            time.sleep(1)
            return "Waiting..."

        # Read image dimensions
        img = cv2.imread(self._screenshot_path)
        img_h, img_w = (img.shape[:2] if img is not None else (1000, 1000))

        if action_type == "hotkey" and text:
            # Optional focus click
            if coordinates and len(coordinates) >= 2 and not isinstance(coordinates[0], list):
                x, y = coordinates
                if not (x == 0 and y == 0):
                    sx, sy = self._map_coordinates(x, y, scale, img_w, img_h, window_offset)
                    pyautogui.click(sx, sy)
                    time.sleep(0.1)

            keys = text.strip().split()
            normalized = []
            for k in keys:
                kl = k.lower()
                if kl in ("win", "meta", "cmd"):
                    normalized.append("command")
                else:
                    normalized.append(kl)
            pyautogui.hotkey(*normalized)
            return f"Hotkey: {'+'.join(normalized)}"

        if action_type == "drag" and isinstance(coordinates[0], list):
            sx, sy = self._map_coordinates(
                coordinates[0][0], coordinates[0][1], scale, img_w, img_h, window_offset
            )
            ex, ey = self._map_coordinates(
                coordinates[1][0], coordinates[1][1], scale, img_w, img_h, window_offset
            )
            pyautogui.moveTo(sx, sy, duration=0.1)
            pyautogui.dragTo(ex, ey, duration=1.0)
            return f"Drag ({sx:.0f},{sy:.0f}) → ({ex:.0f},{ey:.0f})"

        # Single-point actions
        if not coordinates or len(coordinates) < 2:
            return "No coordinates provided"

        x, y = coordinates[:2]
        sx, sy = self._map_coordinates(x, y, scale, img_w, img_h, window_offset)
        pyautogui.moveTo(sx, sy, duration=0.1)

        if action_type == "click":
            pyautogui.click()
        elif action_type == "double_click":
            pyautogui.doubleClick()
        elif action_type == "right_click":
            pyautogui.rightClick()
        elif action_type == "scroll_up":
            pyautogui.scroll(500)
        elif action_type == "scroll_down":
            pyautogui.scroll(-500)
        elif action_type == "input":
            pyautogui.click()
            time.sleep(0.3)
        else:
            return f"Unknown action: {action_type}"

        result = f"{action_type} at ({sx:.0f}, {sy:.0f})"

        # Text input via clipboard paste
        if text and action_type != "hotkey":
            time.sleep(0.5)
            pyperclip.copy(text)
            time.sleep(0.1)
            pyautogui.keyDown("command")
            time.sleep(0.1)
            pyautogui.press("v")
            time.sleep(0.1)
            pyautogui.keyUp("command")
            result += f" + typed '{text[:50]}'"

        time.sleep(0.8)
        return result

    def run(self, objective: str) -> str:
        """Execute the vision-based automation loop.

        Args:
            objective: Natural language description of what to accomplish.

        Returns:
            Final status message.
        """
        self._history = []
        self._should_exit = False
        start_time = time.time()
        last_action = None
        loop_count = 0
        results = []

        for iteration in range(self.max_iterations):
            if time.time() - start_time > self.timeout:
                return f"Timeout after {self.timeout}s ({iteration} iterations)"

            try:
                scale, window_offset = self._capture_screen()
                ai_text = self._call_vision_llm(objective)
                parsed = self._parse_response(ai_text)

                status = parsed.get("status", "in_progress")
                description = parsed.get("description", "")
                action = parsed.get("action", {})

                if status == "completed":
                    return f"Completed: {description}"
                if status == "failed":
                    return f"Failed: {description}"

                # Loop detection
                if action == last_action:
                    loop_count += 1
                    if loop_count >= 3:
                        return f"Stopped: action loop detected after {iteration + 1} iterations"
                else:
                    loop_count = 0
                    last_action = action

                result = self._execute_action(action, scale, window_offset)
                results.append(f"[{iteration + 1}] {description} → {result}")

            except KeyboardInterrupt:
                return "Interrupted by user"
            except Exception as e:
                results.append(f"[{iteration + 1}] Error: {e}")
                time.sleep(2)

        return f"Reached max iterations ({self.max_iterations}). Last actions:\n" + "\n".join(results[-3:])
