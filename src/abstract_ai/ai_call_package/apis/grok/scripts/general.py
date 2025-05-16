import requests
import json

# API endpoint
url = "https://api.x.ai/v1/chat/completions"

# Your API key
api_key = "your_api_key_here"  # Replace with your actual API key

# Headers
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

# Payload
payload = {
    "messages": [
        {
            "role": "system",
            "content": "You are a test assistant."
        },
        {
            "role": "user",
            "content": "Testing. Just say hi and hello world and nothing else."
        }
    ],
    "model": "grok-3-latest",
    "stream": False,
    "temperature": 0
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Check if the request was successful
if response.status_code == 200:
    # Parse and print the response
    result = response.json()
    print(result["choices"][0]["message"]["content"])
else:
    print(f"Error: {response.status_code} - {response.text}")
