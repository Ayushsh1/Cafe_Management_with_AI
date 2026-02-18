import os
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List

import requests

def _summarize_recent_orders(orders: List[Dict], days: int = 7, max_items: int = 5) -> Dict:
    cutoff_date = datetime.now().date() - timedelta(days=days - 1)
    recent_orders = []
    for order in orders:
        order_date = order.get("date")
        if not order_date:
            continue
        try:
            parsed_date = datetime.fromisoformat(order_date).date()
        except ValueError:
            continue
        if parsed_date >= cutoff_date:
            recent_orders.append(order)

    total_orders = len(recent_orders)
    total_revenue = sum(order.get("total", 0) for order in recent_orders)
    item_counter = Counter()
    for order in recent_orders:
        for item in order.get("items", []):
            item_counter[item.get("name", "Unknown")] += item.get("quantity", 0)

    top_items = item_counter.most_common(max_items)
    return {
        "days": days,
        "orders": total_orders,
        "revenue": round(total_revenue, 2),
        "top_items": top_items,
    }

def _build_specials_guidance(menu_items: List[Dict], inventory: List[Dict]) -> str:
    low_stock_items = [
        item.get("name")
        for item in inventory
        if item.get("quantity", 0) <= item.get("reorder_level", 0)
    ]
    low_stock_text = ", ".join(low_stock_items) if low_stock_items else "None"

    available_items = [
        item.get("name")
        for item in menu_items
        if item.get("is_active") and item.get("name") not in low_stock_items
    ]
    available_text = ", ".join(available_items[:8]) if available_items else "None"

    return (
        "Specials & upsell template:\n"
        f"- Avoid low-stock items: {low_stock_text}.\n"
        "- Prioritize items with healthy stock.\n"
        "- For specials: suggest 1-2 beverages + 1 food item.\n"
        "- For upsells: suggest a complementary pastry/snack or size upgrade.\n"
        f"- Suggested in-stock items to highlight: {available_text}."
    )

def _build_context(menu_items: List[Dict], inventory: List[Dict], orders: List[Dict]) -> str:
    menu_lines = [
        f"- {item.get('name')} ({item.get('category', 'Uncategorized')}): ${item.get('price', 0)}"
        for item in menu_items
    ]
    inventory_lines = [
        f"- {item.get('name')}: {item.get('quantity')} {item.get('unit', '')} (reorder at {item.get('reorder_level')})"
        for item in inventory
    ]

    menu_text = "\n".join(menu_lines) if menu_lines else "No menu items available."
    inventory_text = "\n".join(inventory_lines) if inventory_lines else "No inventory items available."

    low_stock_items = [
        item.get("name")
        for item in inventory
        if item.get("quantity", 0) <= item.get("reorder_level", 0)
    ]
    low_stock_text = ", ".join(low_stock_items) if low_stock_items else "None"

    trends = _summarize_recent_orders(orders)
    if trends["top_items"]:
        top_items_lines = "\n".join(
            f"- {name}: {quantity}" for name, quantity in trends["top_items"]
        )
    else:
        top_items_lines = "No recent order data."

    specials_guidance = _build_specials_guidance(menu_items, inventory)

    return (
        "Use the following cafe context to answer questions. "
        "If the answer is not in the context, say you don't have that information.\n\n"
        f"Menu Items:\n{menu_text}\n\n"
        f"Inventory Levels:\n{inventory_text}\n\n"
        f"Low Stock Items: {low_stock_text}\n\n"
        "Recent Order Trends:\n"
        f"- Last {trends['days']} days orders: {trends['orders']}\n"
        f"- Revenue: ${trends['revenue']}\n"
        f"- Top items:\n{top_items_lines}\n\n"
        f"{specials_guidance}"
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

def generate_response(prompt: str, menu_items: List[Dict], inventory: List[Dict], orders: List[Dict]) -> str:
    context = _build_context(menu_items, inventory, orders)
    try:
        return _call_copilot_api(prompt, context)
    except Exception:
        return "I'm running in offline mode. Please configure the Copilot API for live responses."