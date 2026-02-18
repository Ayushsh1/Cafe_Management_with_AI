1| import os
2| from datetime import datetime
3| 
4| import pandas as pd
5| import streamlit as st
6| from dotenv import load_dotenv
7| 
8| from services.analytics import inventory_alerts, summarize_daily_sales
9| from services.ai_assistant import generate_response
10| from services.storage import load_json, save_json
11| 
12| load_dotenv()
13| 
14| st.set_page_config(page_title="Cafe Management with AI", layout="wide")
15| 
16| MENU_FILE = "menu.json"
17| ORDERS_FILE = "orders.json"
18| INVENTORY_FILE = "inventory.json"
19| 
20| menu_items = load_json(MENU_FILE, [])
21| orders = load_json(ORDERS_FILE, [])
22| inventory = load_json(INVENTORY_FILE, [])
23| 
24| st.title("Cafe Management with AI")
25| 
26| pages = [
27|     "Dashboard",
28|     "Menu",
29|     "Orders",
30|     "Inventory",
31|     "AI Assistant",
32| ]
33| 
34| page = st.sidebar.radio("Navigate", pages)
35| 
36| if page == "Dashboard":
37|     st.subheader("Daily Summary")
38|     summary = summarize_daily_sales(orders)
39|     col1, col2, col3 = st.columns(3)
40|     col1.metric("Orders", summary["orders"])
41|     col2.metric("Revenue", f"${summary['revenue']}")
42|     col3.metric("Date", summary["date"])
43| 
44|     st.subheader("Top Items")
45|     if summary["top_items"]:
46|         df = pd.DataFrame(summary["top_items"], columns=["Item", "Quantity"])
47|         st.dataframe(df, use_container_width=True)
48|     else:
49|         st.info("No orders yet today.")
50| 
51|     st.subheader("Low Stock Alerts")
52|     alerts = inventory_alerts(inventory)
53|     if alerts:
54|         st.dataframe(pd.DataFrame(alerts), use_container_width=True)
55|     else:
56|         st.success("All inventory levels look good.")
57| 
58| elif page == "Menu":
59|     st.subheader("Menu Items")
60|     st.dataframe(pd.DataFrame(menu_items), use_container_width=True)
61| 
62|     st.subheader("Add / Update Item")
63|     with st.form("menu_form"):
64|         item_id = st.text_input("Item ID")
65|         name = st.text_input("Name")
66|         category = st.text_input("Category")
67|         price = st.number_input("Price", min_value=0.0, step=0.25)
68|         is_active = st.checkbox("Active", value=True)
69|         submitted = st.form_submit_button("Save")
70| 
71|         if submitted and item_id:
72|             existing = next((item for item in menu_items if item["id"] == item_id), None)
73|             if existing:
74|                 existing.update({"name": name, "category": category, "price": price, "is_active": is_active})
75|             else:
76|                 menu_items.append({
77|                     "id": item_id,
78|                     "name": name,
79|                     "category": category,
80|                     "price": price,
81|                     "is_active": is_active,
82|                 })
83|             save_json(MENU_FILE, menu_items)
84|             st.success("Menu item saved.")
85| 
86| elif page == "Orders":
87|     st.subheader("Create Order")
88|     active_items = [item for item in menu_items if item.get("is_active")]
89|     item_lookup = {item["name"]: item for item in active_items}
90|     selected_items = st.multiselect("Select items", list(item_lookup.keys()))
91|     quantities = {}
92|     for name in selected_items:
93|         quantities[name] = st.number_input(f"Quantity for {name}", min_value=1, value=1, step=1)
94| 
95|     if st.button("Submit Order") and selected_items:
96|         order_items = []
97|         total = 0
98|         for name in selected_items:
99|             item = item_lookup[name]
100|             qty = quantities[name]
101|             total += item["price"] * qty
102|             order_items.append({"id": item["id"], "name": name, "price": item["price"], "quantity": qty})
103|         order = {
104|             "id": f"order-{len(orders) + 1}",
105|             "date": datetime.now().date().isoformat(),
106|             "time": datetime.now().strftime("%H:%M"),
107|             "items": order_items,
108|             "total": round(total, 2),
109|         }
110|         orders.append(order)
111|         save_json(ORDERS_FILE, orders)
112|         st.success(f"Order saved. Total: ${order['total']}")
113| 
114|     st.subheader("Recent Orders")
115|     if orders:
116|         st.dataframe(pd.DataFrame(orders), use_container_width=True)
117|     else:
118|         st.info("No orders yet.")
119| 
120| elif page == "Inventory":
121|     st.subheader("Inventory")
122|     st.dataframe(pd.DataFrame(inventory), use_container_width=True)
123| 
124|     st.subheader("Update Inventory")
125|     with st.form("inventory_form"):
126|         item_id = st.text_input("Item ID")
127|         name = st.text_input("Name")
128|         unit = st.text_input("Unit")
129|         quantity = st.number_input("Quantity", min_value=0.0, step=0.5)
130|         reorder_level = st.number_input("Reorder Level", min_value=0.0, step=0.5)
131|         submitted = st.form_submit_button("Save")
132| 
133|         if submitted and item_id:
134|             existing = next((item for item in inventory if item["id"] == item_id), None)
135|             if existing:
136|                 existing.update({
137|                     "name": name,
138|                     "unit": unit,
139|                     "quantity": quantity,
140|                     "reorder_level": reorder_level,
141|                 })
142|             else:
143|                 inventory.append({
144|                     "id": item_id,
145|                     "name": name,
146|                     "unit": unit,
147|                     "quantity": quantity,
148|                     "reorder_level": reorder_level,
149|                 })
150|             save_json(INVENTORY_FILE, inventory)
151|             st.success("Inventory item saved.")
152| 
153| elif page == "AI Assistant":
154|     st.subheader("AI Assistant")
155|     prompt = st.text_area("Ask a question")
156|     if st.button("Get Response") and prompt:
157|         with st.spinner("Thinking..."):
158|             response = generate_response(prompt, menu_items, inventory)
159|         st.write(response)
160| 
161| st.sidebar.markdown("---")
162| st.sidebar.caption("Cafe Management with AI")