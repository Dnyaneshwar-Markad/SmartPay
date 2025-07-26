import streamlit as st
import json
from reminders.reminder_engine import generate_reminders
# from data_engine.budget_handler import get_user_budget  # if you have a separate module for this
import sqlite3
import pandas as pd
import os 

# DB Path
DB_PATH = os.path.join(os.path.dirname(__file__), '../security/smartpay.db')

# Connect to DB
conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM transactions", conn)


# Ask user for monthly budget
st.sidebar.header("💰 Set Your Monthly Budget")
monthly_budget = st.sidebar.number_input("Enter your total monthly budget (Rs.):", min_value=1000, step=500)

# To generate reminders
PARSED_JSON_PATH = os.path.join(os.path.dirname(__file__), '../sms_email_parser/parsed_output.json')
with open(PARSED_JSON_PATH, "r") as f:
    transactions = json.load(f)
# ✅ Convert to DataFrame
pdf = pd.DataFrame(transactions)
reminders = generate_reminders(pdf, monthly_budget)
st.sidebar.markdown("## 🔔 Notifications")
with st.sidebar.expander("🔔 View Notifications", expanded=True):
    if reminders:
        for reminder in reminders:
            st.sidebar.markdown(f"""
            **{reminder['type']}**
            - {reminder['message']}
            - 📅 `{reminder['date']}`
            - ⚠️ Priority: `{reminder['priority']}`
            ---
            """)
    else:
        st.sidebar.success("🎉 No new reminders!")

# Budget split based on percentage
budget_split = {
    "Groceries": 0.20,
    "Food": 0.15,
    "Bills": 0.20,
    "Travel": 0.10,
    "Shopping": 0.20,
    "Entertainment": 0.05,
    "Other": 0.10
}

default_budgets = {category: round(monthly_budget * pct, 2) for category, pct in budget_split.items()}

# Title and summary
st.title("💰 SmartPay Dashboard")
st.subheader("Track your expenses, subscriptions, and financial health")

st.sidebar.header("🔍 Filter Transactions")

# Unique merchants and categories
merchants = df["merchant"].dropna().unique().tolist()
categories = df["category"].dropna().unique().tolist()

# Date filters
min_date = pd.to_datetime(df["date"]).min()
max_date = pd.to_datetime(df["date"]).max()

date_range = st.sidebar.date_input("📅 Select Date Range", [min_date, max_date])

# Merchant and category filters
selected_merchants = st.sidebar.multiselect("🏬 Select Merchants", merchants, default=merchants)
selected_categories = st.sidebar.multiselect("📂 Select Categories", categories, default=categories)

# Convert date to datetime
df["date"] = pd.to_datetime(df["date"])

# Apply filters
filtered_df = df[
    (df["date"] >= pd.to_datetime(date_range[0])) &
    (df["date"] <= pd.to_datetime(date_range[1])) &
    (df["merchant"].isin(selected_merchants)) &
    (df["category"].isin(selected_categories))
]

# Show recent transactions
st.write("### 🧾 Recent Transactions")
st.dataframe(filtered_df.sort_values(by="date", ascending=False).head(10))

# Show total spend
total = filtered_df["amount"].sum()
st.metric("Total Spent", f"Rs. {total:,.2f}")

# Actual vs Budget Comparison
st.subheader("📊 Budget vs Actual (This Month)")

import datetime

## Current month filter
current_month = pd.to_datetime("today").to_period("M")
monthly_df = filtered_df[filtered_df["date"].dt.to_period("M") == current_month]

## Group actuals
actuals = monthly_df.groupby("category")["amount"].sum()

## Create DataFrame for comparison
budget_data = []
for category, budget in default_budgets.items():
    actual = actuals.get(category, 0)
    variance = actual - budget
    status = "✅ Within Budget" if variance <= 0 else "⚠️ Over Budget"
    budget_data.append({
        "Category": category,
        "Budget (Rs.)": budget,
        "Spent (Rs.)": round(actual, 2),
        "Variance (Rs.)": round(variance, 2),
        "Status": status
    })

# Total spent
total_spent = filtered_df[filtered_df["date"].dt.to_period("M") == current_month]["amount"].sum()
savings = monthly_budget - total_spent

# Add to the budget_data
budget_data.append({
    "Category": "Savings This Month",
    "Budget (Rs.)": "-",
    "Spent (Rs.)": "-",
    "Variance (Rs.)": round(savings, 2),
    "Status": "💰 Saved" if savings >= 0 else "🚨 Overspent"
})

st.dataframe(pd.DataFrame(budget_data))

# Budget Advice Recommendation
st.markdown("### 📊 Budget Advice")

if savings > 0:
    st.success(f"Great job! You're ₹{round(savings, 2)} under your budget this month. Keep tracking your spending to increase your savings further.")
    
    # Extra tip
    if savings > 0.15 * monthly_budget:
        st.info("Tip: Consider investing your savings or setting aside a portion as an emergency fund.")
else:
    st.error(f"You've overspent by ₹{abs(round(savings, 2))} this month. Try reviewing high-spend categories like Shopping or Food.")

    # Suggest top overspent category
    overspent = filtered_df.groupby("category")["amount"].sum().reset_index()
    overspent = overspent.merge(pd.DataFrame(default_budgets.items(), columns=["category", "budget"]), on="category")
    overspent["diff"] = overspent["amount"] - overspent["budget"]
    overspent = overspent.sort_values("diff", ascending=False)

    if not overspent.empty and overspent.iloc[0]["diff"] > 0:
        cat = overspent.iloc[0]["category"]
        amt = overspent.iloc[0]["diff"]
        st.warning(f"You're overspending most in **{cat}** by ₹{round(amt, 2)}. Consider reducing expenses there next month.")

# Pie Chart for Spend Distribution
import plotly.express as px
st.subheader("💸 Spend Distribution by Category")

if not filtered_df.empty and "category" in filtered_df.columns:
    category_summary = filtered_df.groupby("category")["amount"].sum().reset_index()
    fig = px.pie(category_summary, values="amount", names="category",
                title="Spending by Category", hole=0.4)
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data available to display pie chart.")

# Spend by merchant
st.write("### 🛍️ Spend by Merchant")
merchant_data = filtered_df.groupby("merchant")["amount"].sum().sort_values(ascending=False).head(5)
st.bar_chart(merchant_data)

# Spend by date
st.write("### 📅 Monthly Spending Trend")
filtered_df['date'] = pd.to_datetime(df['date'])
monthly = df.groupby(filtered_df['date'].dt.to_period("M"))["amount"].sum()
monthly.index = monthly.index.astype(str)
st.line_chart(monthly)
