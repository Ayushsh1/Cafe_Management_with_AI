import os
from datetime import datetime

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from services.analytics import inventory_alerts, summarize_daily_sales
from services.ai_assistant import generate_response
from services.storage import load_json, save_json

load_dotenv()

st.set_page_config(page_title="Cafe Management with AI", layout="wide")

MENU_FILE = "menu.json"
ORDERS_FILE = "orders.json"
INVENTORY_FILE = "inventory.json"

menu_items = load_json(MENU_FILE, [])
orders = load_json(ORDERS_FILE, [])
inventory = load_json(INVENTORY_FILE, [])

st.title("Cafe Management with AI")

pages = [
    "Dashboard",
    "Menu",
    "Orders",
    "Inventory",
    "AI Assistant",
]

page = st.sidebar.radio("Navigate", pages)

if page == "Dashboard":
    st.subheader("Daily Summary")
    summary = summarize_daily_sales(orders)
    col1, col2, col3 = st.columns(3)
    col1.metric("Orders", summary["orders"])
    col2.metric("Revenue", f"${summary['revenue']}")
    col3.metric("Date", summary["date"])

    st.subheader("Top Items")
    if summary["top_items"]:
        df = pd.DataFrame(summary["top_items"], columns=["Item", "Quantity"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No orders yet today.")

    st.subheader("Low Stock Alerts")
    alerts = inventory_alerts(inventory)
    if alerts:
        st.dataframe(pd.DataFrame(alerts), use_container_width=True)
    else:
        st.success("All inventory levels look good.")

elif page == "Menu":
    st.subheader("Menu Items")
    st.dataframe(pd.DataFrame(menu_items), use_container_width=True)

    st.subheader("Add / Update Item")
    with st.form("menu_form"):
        item_id = st.text_input("Item ID")
        name = st.text_input("Name")
        category = st.text_input("Category")
        price = st.number_input("Price", min_value=0.0, step=0.25)
        is_active = st.checkbox("Active", value=True)
        submitted = st.form_submit_button("Save")

        if submitted and item_id:
            existing = next((item for item in menu_items if item["id"] == item_id), None)
            if existing:
                existing.update({"name": name, "category": category, "price": price, "is_active": is_active})
            else:
                menu_items.append({
                    "id": item_id,
                    "name": name,
                    "category": category,
                    "price": price,
                    "is_active": is_active,
                })
            save_json(MENU_FILE, menu_items)
            st.success("Menu item saved.")

elif page == "Orders":
    st.subheader("Create Order")
    active_items = [item for item in menu_items if item.get("is_active")]
    item_lookup = {item["name"]: item for item in active_items}
    selected_items = st.multiselect("Select items", list(item_lookup.keys()))
    quantities = {}
    for name in selected_items:
        quantities[name] = st.number_input(f"Quantity for {name}", min_value=1, value=1, step=1)

    if st.button("Submit Order") and selected_items:
        order_items = []
        total = 0
        for name in selected_items:
            item = item_lookup[name]
            qty = quantities[name]
            total += item["price"] * qty
            order_items.append({"id": item["id"], "name": name, "price": item["price"], "quantity": qty})
        order = {
            "id": f"order-{len(orders) + 1}",
            "date": datetime.now().date().isoformat(),
            "time": datetime.now().strftime("%H:%M"),
            "items": order_items,
            "total": round(total, 2),
        }
        orders.append(order)
        save_json(ORDERS_FILE, orders)
        st.success(f"Order saved. Total: ${order['total']}")

    st.subheader("Recent Orders")
    if orders:
        st.dataframe(pd.DataFrame(orders), use_container_width=True)
    else:
        st.info("No orders yet.")

elif page == "Inventory":
    st.subheader("Inventory")
    st.dataframe(pd.DataFrame(inventory), use_container_width=True)

    st.subheader("Update Inventory")
    with st.form("inventory_form"):
        item_id = st.text_input("Item ID")
        name = st.text_input("Name")
        unit = st.text_input("Unit")
        quantity = st.number_input("Quantity", min_value=0.0, step=0.5)
        reorder_level = st.number_input("Reorder Level", min_value=0.0, step=0.5)
        submitted = st.form_submit_button("Save")

        if submitted and item_id:
            existing = next((item for item in inventory if item["id"] == item_id), None)
            if existing:
                existing.update({
                    "name": name,
                    "unit": unit,
                    "quantity": quantity,
                    "reorder_level": reorder_level,
                })
            else:
                inventory.append({
                    "id": item_id,
                    "name": name,
                    "unit": unit,
                    "quantity": quantity,
                    "reorder_level": reorder_level,
                })
            save_json(INVENTORY_FILE, inventory)
            st.success("Inventory item saved.")

elif page == "AI Assistant":
    st.subheader("AI Assistant")
    prompt = st.text_area("Ask a question")
    if st.button("Get Response") and prompt:
        with st.spinner("Thinking..."):
            response = generate_response(prompt)
        st.write(response)

st.sidebar.markdown("---")
st.sidebar.caption("Cafe Management with AI")
