import os
from typing import List, Dict

import requests

def _build_context(menu_items: List[Dict], inventory: List[Dict]) -> str:
    menu_lines = []
    for item in menu_items:
        menu_lines.append(
            f"- {item.get('name')} ({item.get('category', 'Uncategorized')}): ${item.get('price', 0)}"
        )

    inventory_lines = []
    for item in inventory:
        inventory_lines.append(
            f"- {item.get('name')}: {item.get('quantity')} {item.get('unit', '')} (reorder at {item.get('reorder_level')})"
        )

    menu_text = "\n".join(menu_lines) if menu_lines else "No menu items available."
    inventory_text = "\n".join(inventory_lines) if inventory_lines else "No inventory items available."

    return (
        "Use the following cafe context to answer questions. "
        "If the answer is not in the context, say you don't have that information.\n\n"
        f"Menu Items:\n{menu_text}\n\nInventory Levels:\n{inventory_text}"
    )

def _call_copilot_api(prompt: str, context: str) -> str:
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
            {
                "role": "system",
                "content": (
                    "You are a helpful cafe assistant. Provide concise, friendly answers. "
                    "Use the provided context and avoid guessing.\n\n"
                    f"{context}"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
        "max_tokens": 300,
    }

    response = requests.post(api_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]

def generate_response(prompt: str, menu_items: List[Dict], inventory: List[Dict]) -> str:
    context = _build_context(menu_items, inventory)
    try:
        return _call_copilot_api(prompt, context)
    except Exception:
        return "I'm running in offline mode. Please configure the Copilot API for live responses."