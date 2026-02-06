#!/usr/bin/env python3
"""Test if zenmux.ai accepts standard Authorization header"""

import requests
import json

api_key = "sk-ai-v1-fc980b71439d46806b57d42acc7e2150117875b8c265504aed04e8c78167dc16"
base_url = "https://zenmux.ai/api/v1"
model = "anthropic/claude-sonnet-4.5"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}",  # Standard format
    "anthropic-version": "2023-06-01"
}

payload = {
    "model": model,
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "Hi!"}
    ]
}

print("Testing with Authorization: Bearer header...")
print(f"URL: {base_url}/messages")
print("=" * 60)

response = requests.post(
    f"{base_url}/messages",
    headers=headers,
    json=payload,
    timeout=30
)

print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✅ SUCCESS! Standard Authorization header works!")
else:
    print(f"❌ Failed: {response.text[:500]}")
