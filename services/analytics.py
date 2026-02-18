from collections import Counter
from datetime import datetime
from typing import Dict, List

def summarize_daily_sales(orders: List[Dict]) -> Dict:
    today = datetime.now().date().isoformat()
    daily_orders = [order for order in orders if order.get("date") == today]
    total_revenue = sum(order.get("total", 0) for order in daily_orders)
    item_counter = Counter()
    for order in daily_orders:
        for item in order.get("items", []):
            item_counter[item["name"]] += item.get("quantity", 0)
    top_items = item_counter.most_common(5)
    return {
        "date": today,
        "orders": len(daily_orders),
        "revenue": round(total_revenue, 2),
        "top_items": top_items,
    }

def inventory_alerts(inventory: List[Dict]) -> List[Dict]:
    return [item for item in inventory if item.get("quantity", 0) <= item.get("reorder_level", 0)]
