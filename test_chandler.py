#!/usr/bin/env python3
"""Quick test script for Chandler configuration."""

import sys
sys.path.insert(0, '/Users/zhaopin/HY/chanlder')

from chandler.brain import Brain
from chandler.config import config

# Import tool modules to register them
import chandler.tools.web_search      # noqa: F401
import chandler.tools.web_browse      # noqa: F401
import chandler.tools.run_python      # noqa: F401
import chandler.tools.run_shell       # noqa: F401
import chandler.tools.file_ops        # noqa: F401
import chandler.tools.system_control  # noqa: F401
import chandler.tools.computer_use    # noqa: F401
import chandler.tools.memory_tools    # noqa: F401

print("=" * 60)
print("Testing Chandler Configuration")
print("=" * 60)
print(f"API Key: {config.api_key[:20]}...")
print(f"Base URL: {config.base_url}")
print(f"Model: {config.claude_model}")
print(f"Max Tokens: {config.max_tokens}")
print("=" * 60)

# Initialize brain and send a simple test message
brain = Brain()
print("\nSending test message: 'Hi, can you introduce yourself?'")
print("-" * 60)

try:
    response = brain.chat("Hi, can you introduce yourself?")
    print("\n✅ SUCCESS! Response received:")
    print("-" * 60)
    print(response)
    print("-" * 60)
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"Message: {str(e)}")
    import traceback
    traceback.print_exc()
