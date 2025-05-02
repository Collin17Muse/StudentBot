# student_finance_dashboard.py

import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import random
import feedparser

st.set_page_config(page_title="College Student Finance Dashboard", layout="wide")

st.title("🎓 College Student Finance Dashboard")
st.markdown("""
This dashboard is tailored for college students looking to:
- Track student-friendly stocks (tech, retail, consumer goods)
- Learn how markets affect budgeting
- Monitor basic budgeting goals and personal expenses
- Understand loan repayments and stay alert on stock drops
- Set and track personal savings goals
- Stay updated with financial news
""")

# Section 1: Track Student-Friendly Stocks
st.header("📈 Track Popular Stocks Among Students")
student_stocks = ["AAPL", "MSFT", "TSLA", "NFLX", "AMZN", "GOOGL"]

@st.cache_data
def fetch_prices(tickers):
    end = datetime.today()
    start = end - timedelta(days=90)
    data = yf.download(tickers, start=start, end=end, group_by='ticker', auto_adjust=True)

    if isinstance(tickers, str):
        return data[['Close']].rename(columns={'Close': 'Adj Close'})
    else:
        return data.loc[:, (slice(None), 'Close')].droplevel(1, axis=1).rename(columns=lambda x: x)

stock_data = fetch_prices(student_stocks)
selected = st.multiselect("Choose stocks to visualize:", student_stocks, default=student_stocks[:2])

if selected:
    st.line_chart(stock_data[selected])
else:
    st.warning("Please select at least one stock to display the chart.")

# Stock Price Drop Alerts
st.subheader("🔔 Stock Price Drop Alerts")
alert_stock = st.selectbox("Select a stock to monitor for price drop alerts:", student_stocks)
drop_threshold = st.slider("Alert if stock falls below ($):", min_value=50, max_value=500, value=100, step=5)
latest_price = stock_data[alert_stock].dropna().iloc[-1] if not stock_data[alert_stock].dropna().empty else None

if latest_price:
    if latest_price < drop_threshold:
        st.error(f"⚠️ Alert: {alert_stock} is now at ${latest_price:.2f}, below your threshold of ${drop_threshold}!")
    else:
        st.success(f"{alert_stock} is currently at ${latest_price:.2f}. No alert triggered.")
else:
    st.warning("No recent price data available.")

# Section 2: Budget Planning
st.header("💰 Monthly Budget Planner")
income = st.number_input("Monthly Income ($):", min_value=0, value=1000, step=100)
rent = st.number_input("Rent ($):", min_value=0, value=500, step=50)
food = st.number_input("Food & Groceries ($):", min_value=0, value=200, step=50)
transport = st.number_input("Transport ($):", min_value=0, value=100, step=25)
other = st.number_input("Other Expenses ($):", min_value=0, value=100, step=25)

total_expense = rent + food + transport + other
savings = income - total_expense

st.subheader("📊 Budget Summary")
st.metric("Total Expenses", f"${total_expense}")
st.metric("Remaining / Savings", f"${savings}", delta=f"{'+' if savings >= 0 else ''}{savings}")

# Pie chart visualization
budget_df = pd.DataFrame({
    'Category': ['Rent', 'Food', 'Transport', 'Other', 'Savings'],
    'Amount': [rent, food, transport, other, max(savings, 0)]
})

st.plotly_chart({
    "data": [
        {
            "type": "pie",
            "labels": budget_df['Category'],
            "values": budget_df['Amount'],
            "hole": .3
        }
    ],
    "layout": {"title": "Monthly Budget Distribution"}
})

# Section 3: Loan Repayment Estimator
st.header("📉 Student Loan Repayment Calculator")
loan_amount = st.number_input("Loan Amount ($):", min_value=0, value=10000, step=500)
annual_rate = st.slider("Interest Rate (%):", min_value=1.0, max_value=15.0, value=5.0, step=0.1)
years = st.slider("Repayment Term (Years):", min_value=1, max_value=30, value=10)

monthly_rate = annual_rate / 100 / 12
num_payments = years * 12
monthly_payment = loan_amount * monthly_rate / (1 - (1 + monthly_rate) ** -num_payments)

total_payment = monthly_payment * num_payments

st.metric("Monthly Payment", f"${monthly_payment:.2f}")
st.metric("Total Repayment", f"${total_payment:.2f}")

# Section 4: Savings Goal Tracker
st.header("🎯 Savings Goal Tracker")
goal_amount = st.number_input("Enter your savings goal ($):", min_value=0, value=5000, step=100)
current_savings = st.number_input("Current savings ($):", min_value=0, value=1000, step=100)
savings_progress = (current_savings / goal_amount) * 100 if goal_amount > 0 else 0

st.progress(min(int(savings_progress), 100))
st.write(f"You're {savings_progress:.1f}% of the way to your goal of ${goal_amount}!")

# Section 5: Student Investor News Feed
st.header("📰 Financial News for Students")
@st.cache_data
def fetch_news():
    feed = feedparser.parse("https://www.investing.com/rss/news_285.rss")
    return feed.entries[:5]

news_items = fetch_news()
for item in news_items:
    st.write(f"**{item.title}**")
    st.write(item.link)
    st.write(f"*Published:* {item.published}")
    st.markdown("---")

# Section 6: Financial Tip
st.header("📘 Financial Tip of the Day")
tips = [
    "Automate your savings by setting up recurring transfers to a savings account.",
    "Use student discounts and cashback tools to save on purchases.",
    "Track every dollar — budgeting apps can help you control impulse spending.",
    "Invest early, even small amounts, to benefit from compound growth.",
    "Pay more than the minimum on student loans to reduce total interest.",
    "Set realistic savings goals and track your progress monthly."
]
st.info(random.choice(tips))
