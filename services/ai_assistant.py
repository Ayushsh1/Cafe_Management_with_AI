import os
import requests

def _call_copilot_api(prompt: str) -> str:
    api_url = os.getenv("COPILOT_API_URL")
    api_token = os.getenv("COPILOT_API_TOKEN")
    model = os.getenv("COPILOT_API_MODEL", "gpt-4o-mini")

    if not api_url or not api_token:
        return "Copilot API is not configured. Please set COPILOT_API_URL and COPILOT_API_TOKEN."

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful cafe assistant."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 300,
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

def generate_response(prompt: str) -> str:
    try:
        return _call_copilot_api(prompt)
    except Exception:
        return "I'm running in offline mode. Please configure the Copilot API for live responses."
