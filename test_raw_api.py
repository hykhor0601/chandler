#!/usr/bin/env python3
"""Test raw API call to zenmux.ai"""

import requests
import json

api_key = "sk-ai-v1-fc980b71439d46806b57d42acc7e2150117875b8c265504aed04e8c78167dc16"
base_url = "https://zenmux.ai/api/v1"
model = "anthropic/claude-sonnet-4.5"

headers = {
    "Content-Type": "application/json",
    "x-api-key": api_key,
    "anthropic-version": "2023-06-01"  # Required by Anthropic API
}

payload = {
    "model": model,
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "Hi, can you introduce yourself?"}
    ]
}

print("Testing with x-api-key header...")
print(f"URL: {base_url}/messages")
print(f"Model: {model}")
print("=" * 60)

response = requests.post(
    f"{base_url}/messages",
    headers=headers,
    json=payload,
    timeout=30
)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text[:500]}")

if response.status_code == 200:
    print("\n✅ SUCCESS with x-api-key!")
    print(json.dumps(response.json(), indent=2)[:1000])
