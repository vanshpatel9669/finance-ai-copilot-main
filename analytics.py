# src/analytics.py
"""
Analytics module for the AI Personal Finance Copilot.

This file contains helper functions used to analyze cleaned (gold-level)
financial transaction data. These analytics power the visual insights
and spending summaries displayed in the Streamlit dashboard.
"""

import pandas as pd
from config import GOLD_PATH


def load_gold(path: str = GOLD_PATH) -> pd.DataFrame:
    """
    Load the gold-level cleaned transaction dataset.

    Parameters
    ----------
    path : str
        File path to the gold dataset CSV.

    Returns
    -------
    pd.DataFrame
        DataFrame containing cleaned and feature-engineered transactions.
    """
    return pd.read_csv(path, parse_dates=["date"])


def monthly_spend_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute total spending amount per category per month.

    This is used for:
    - Monthly trend charts
    - Category-wise spending comparisons over time

    Parameters
    ----------
    df : pd.DataFrame
        Gold-level transaction data.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: [month, category, amount]
    """
    return (
        df.groupby([df["date"].dt.to_period("M"), "category"])["amount"]
          .sum()
          .reset_index()
          .rename(columns={"date": "month"})
    )


def total_spend_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate total lifetime spending per category.

    This is used for:
    - Category breakdown bar charts
    - High-level budget summaries
    - Insights on where the user spends the most

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    pd.DataFrame
        Sorted summary of total spend per category.
    """
    return (
        df.groupby("category")["amount"]
          .sum()
          .reset_index()
          .sort_values("amount", ascending=False)
    )


def recurring_merchants(df: pd.DataFrame, min_transactions: int = 3) -> pd.DataFrame:
    """
    Identify recurring merchants — merchants where the user transacted
    at least `min_transactions` times.

    These may indicate:
    - Subscriptions
    - Frequent habit-based spending
    - Regular bills (utilities, groceries)

    Parameters
    ----------
    df : pd.DataFrame
    min_transactions : int
        Minimum number of transactions to classify as recurring.

    Returns
    -------
    pd.DataFrame
        Merchants with N+ transactions and total spending amounts.
    """
    grp = df.groupby("merchant").agg(
        n_txn=("merchant", "size"),
        total_spent=("amount", "sum")
    )
    return grp[grp["n_txn"] >= min_transactions].sort_values("n_txn", ascending=False)


def efficiency_score(df: pd.DataFrame) -> float:
    """
    Compute a simple spending efficiency score (0–100).

    The score penalizes spending in “non-essential” categories such as:
    - shopping
    - misc_net
    - misc_pos

    You can refine this later to incorporate:
    - income estimates
    - savings rate
    - monthly budgets
    - category weighting

    Parameters
    ----------
    df : pd.DataFrame

    Returns
    -------
    float
        Efficiency score where a higher value indicates more “efficient”
        or intentional spending.
    """
    total = df["amount"].sum()
    if total == 0:
        return 100.0  # No spending → perfect score

    bad_cats = ["shopping", "misc_net", "misc_pos"]
    mask = df["category"].str.lower().isin(bad_cats)

    bad_share = df.loc[mask, "amount"].sum() / total
    score = max(0, 100 * (1 - bad_share))

    return round(score, 2)
