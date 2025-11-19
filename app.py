# app.py
import streamlit as st
import pandas as pd

from config import GOLD_PATH
from analytics import (
    load_gold, total_spend_summary,
    monthly_spend_by_category, recurring_merchants,
    efficiency_score
)
from model import load_model

@st.cache_data
def get_gold_data():
    return load_gold(GOLD_PATH)

@st.cache_resource
def get_model():
    return load_model()

def main():
    st.title("AI Personal Finance Copilot 💸")
    st.write("Analyze your transactions, detect patterns, and get smart insights.")

    df = get_gold_data()
    model = get_model()

    # Overview 
    st.header("Overview")
    st.write(f"Total transactions: {len(df):,}")
    st.write(f"Date range: {df['date'].min().date()} → {df['date'].max().date()}")
    st.metric("Financial Efficiency Score", f"{efficiency_score(df)} / 100")

    # Category Summary 
    st.header("Spending by Category")
    cat_summary = total_spend_summary(df)
    st.dataframe(cat_summary)
    st.bar_chart(cat_summary.set_index("category"))

    #  Monthly Trends 
    st.header("Monthly Spend by Category")
    monthly = monthly_spend_by_category(df)
    pivot = monthly.pivot(index="month", columns="category", values="amount").fillna(0)
    st.line_chart(pivot)

    #  Recurring Merchants 
    st.header("Recurring Merchants (Potential Subscriptions)")
    rec = recurring_merchants(df, min_transactions=5).head(20)
    st.dataframe(rec)

    #  Try the classifier on a new transaction 
    st.header("Try a New Transaction")
    desc = st.text_input("Transaction description", "NETFLIX.COM Subscription")
    if st.button("Predict Category"):
        pred = model.predict([desc])[0]
        st.success(f"Predicted category: **{pred}**")

if __name__ == "__main__":
    main()