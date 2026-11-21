import streamlit as st
import pandas as pd
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="IT Mart - Online Store & Inventory", page_icon="🛒", layout="wide")

# Initialize Session State for Inventory, Cart, and Orders
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        "P101": {"name": "Basmati Rice (1kg)", "category": "Grains", "price": 85, "stock": 50, "img": "🌾"},
        "P102": {"name": "Sugar (1kg)", "category": "Groceries", "price": 45, "stock": 40, "img": "🍚"},
        "P103": {"name": "Sunflower Oil (1L)", "category": "Oil & Ghee", "price": 135, "stock": 30, "img": "🌻"},
        "P104": {"name": "Toor Dal (1kg)", "category": "Grains", "price": 160, "stock": 25, "img": "🥣"},
        "P105": {"name": "Tea Powder (500g)", "category": "Beverages", "price": 210, "stock": 20, "img": "☕"},
        "P106": {"name": "Wheat Flour (5kg)", "category": "Grains", "price": 240, "stock": 15, "img": "🥖"},
    }

if 'cart' not in st.session_state:
    st.session_state.cart = {}

if 'orders' not in st.session_state:
    st.session_state.orders = []

# Sidebar Navigation
st.sidebar.title("🛒 IT Mart")
st.sidebar.caption("Smart Supermarket & Inventory System")
menu = st.sidebar.radio("Navigation:", ["🛍️ Store (Shop Online)", "🧾 Cart & Checkout", "📦 Inventory Management (Admin)"])

# ---------------------------------------------------------
# 1. CUSTOMER STOREFRONT (Amazon-style Shopping)
# ---------------------------------------------------------
if menu == "🛍️ Store (Shop Online)":
    st.title("🛍️ Welcome to IT Mart")
    st.write("Browse products, add them to your cart, and checkout seamlessly.")
    
    # Search and Category Filter
    col_s1, col_s2 = st.columns([2, 1])
    search_query = col_s1.text_input("🔍 Search products (e.g., Rice, Oil, Tea...)", "")
    categories = ["All"] + list(set(item["category"] for item in st.session_state.inventory.values()))
    selected_cat = col_s2.selectbox("Filter by Category:", categories)

    st.divider()

    # Display Product Cards in a 3-column Grid
    cols = st.columns(3)
    idx = 0
    for pid, item in st.session_state.inventory.items():
        if search_query.lower() in item["name"].lower() and (selected_cat == "All" or item["category"] == selected_cat):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.subheader(f"{item['img']} {item['name']}")
                    st.caption(f"Category: {item['category']} | ID: {pid}")
                    st.markdown(f"**Price: ₹{item['price']}**")
                    
                    if item["stock"] > 0:
                        st.success(f"In Stock: {item['stock']} units")
                        qty = st.number_input("Quantity", min_value=1, max_value=item["stock"], value=1, key=f"qty_{pid}")
                        if st.button("🛒 Add to Cart", key=f"btn_{pid}", use_container_width=True):
                            if pid in st.session_state.cart:
                                st.session_state.cart[pid]["qty"] += qty
                            else:
                                st.session_state.cart[pid] = {
                                    "name": item["name"],
                                    "price": item["price"],
                                    "qty": qty
                                }
                            st.toast(f"✅ Added {item['name']} to your cart!")
                    else:
                        st.error("❌ Out of Stock")
            idx += 1

# ---------------------------------------------------------
# 2. CART, PAYMENT & ONLINE BILLING
# ---------------------------------------------------------
elif menu == "🧾 Cart & Checkout":
    st.title("🧾 Your Shopping Cart & Checkout")
    
    if not st.session_state.cart:
        st.info("Your cart is currently empty. Go to 'Store (Shop Online)' to add items.")
    else:
        cart_items = []
        subtotal = 0
        for pid, c_item in st.session_state.cart.items():
            total_price = c_item["price"] * c_item["qty"]
            subtotal += total_price
            cart_items.append({
                "Product ID": pid,
                "Item Name": c_item["name"],
                "Unit Price (₹)": c_item["price"],
                "Quantity": c_item["qty"],
                "Total (₹)": total_price
            })
        
        st.table(pd.DataFrame(cart_items))
        
        gst = round(subtotal * 0.05, 2)  # 5% GST
        grand_total = subtotal + gst
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Customer Details")
            cust_name = st.text_input("Full Name*", placeholder="e.g., Rahul Patil")
            cust_phone = st.text_input("Mobile Number*", placeholder="e.g., 9876543210")
            pay_mode = st.selectbox("Select Payment Method:", ["UPI (GPay / PhonePe / Paytm)", "Debit / Credit Card", "Cash on Delivery (COD)"])
        
        with col2:
            st.subheader("Order Summary")
            st.write(f"Subtotal: **₹{subtotal}**")
            st.write(f"GST (5%): **₹{gst}**")
            st.markdown(f"### Grand Total: ₹{grand_total}")
            
            if st.button("✅ Pay Now & Generate Bill", type="primary", use_container_width=True):
                if not cust_name or not cust_phone:
                    st.warning("Please enter customer name and mobile number!")
                else:
                    # Deduct purchased quantity from Inventory
                    for pid, c_item in st.session_state.cart.items():
                        st.session_state.inventory[pid]["stock"] -= c_item["qty"]
                    
                    # Save Order Record
                    order_id = f"ITM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    order_data = {
                        "order_id": order_id,
                        "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
                        "customer": cust_name,
                        "phone": cust_phone,
                        "payment": pay_mode,
                        "items": cart_items,
                        "subtotal": subtotal,
                        "gst": gst,
                        "total": grand_total
                    }
                    st.session_state.orders.append(order_data)
                    st.session_state.cart = {}  # Clear Cart
                    
                    st.success(f"🎉 Payment Successful! Order ID: **{order_id}**")
                    
                    # Generate Digital Invoice
                    bill_text = f"""
=========================================
          🛒 IT MART - INVOICE
=========================================
Invoice No: {order_id}
Date:       {order_data['date']}
Customer:   {cust_name} ({cust_phone})
Payment:    {pay_mode}
-----------------------------------------
Item                   Qty      Amount
-----------------------------------------
"""
                    for item in cart_items:
                        bill_text += f"{item['Item Name']:<22} x{item['Quantity']:<7} ₹{item['Total (₹)']}\n"
                    
                    bill_text += f"""-----------------------------------------
Subtotal:                       ₹{subtotal}
GST (5%):                       ₹{gst}
Grand Total:                    ₹{grand_total}
=========================================
     Thank you for shopping at IT Mart!
=========================================
"""
                    st.code(bill_text, language="text")
                    st.download_button("📥 Download Invoice (.txt)", bill_text, file_name=f"{order_id}.txt")

        if st.button("🗑️ Clear Cart"):
            st.session_state.cart = {}
            st.rerun()

# ---------------------------------------------------------
# 3. INVENTORY MANAGEMENT (Admin Dashboard)
# ---------------------------------------------------------
elif menu == "📦 Inventory Management (Admin)":
    st.title("📦 IT Mart - Inventory & Sales Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["📊 Current Stock", "➕ Add New Product", "📜 Sales History"])
    
    # Tab 1: Current Stock & Restock
    with tab1:
        st.subheader("Live Store Inventory")
        inv_list = []
        for pid, item in st.session_state.inventory.items():
            status = "🟢 In Stock" if item["stock"] > 10 else ("🟡 Low Stock" if item["stock"] > 0 else "🔴 Out of Stock")
            inv_list.append({
                "Product ID": pid,
                "Product Name": item["name"],
                "Category": item["category"],
                "Price (₹)": item["price"],
                "Available Stock": item["stock"],
                "Status": status
            })
        st.dataframe(pd.DataFrame(inv_list), use_container_width=True)
        
        st.subheader("Restock Existing Item")
        c1, c2, c3 = st.columns(3)
        upd_id = c1.selectbox("Select Product:", list(st.session_state.inventory.keys()), format_func=lambda x: f"{x} - {st.session_state.inventory[x]['name']}")
        add_qty = c2.number_input("Quantity to Add:", min_value=1, value=10)
        if c3.button("Update Stock", use_container_width=True):
            st.session_state.inventory[upd_id]["stock"] += add_qty
            st.success(f"✅ Stock updated for {st.session_state.inventory[upd_id]['name']}!")
            st.rerun()

    # Tab 2: Add New Product
    with tab2:
        st.subheader("Add New Product to IT Mart")
        with st.form("add_product_form"):
            new_id = st.text_input("Product ID (e.g., P107)")
            new_name = st.text_input("Product Name (e.g., Peanuts 1kg)")
            new_cat = st.selectbox("Category", ["Grains", "Groceries", "Oil & Ghee", "Beverages", "Snacks", "Electronics", "Other"])
            new_price = st.number_input("Price (₹)", min_value=1, value=50)
            new_stock = st.number_input("Initial Stock", min_value=1, value=20)
