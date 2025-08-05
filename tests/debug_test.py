#!/usr/bin/env python3

import requests
import json

# Test directo al endpoint
url = "http://localhost:8000/api/chat/completion"
data = {
    "messages": [
        {"role": "user", "content": "Hello"}
    ]
}

try:
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code != 200:
        print(f"Headers: {response.headers}")
except Exception as e:
    print(f"Error: {e}")