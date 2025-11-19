# src/analytics.py
import pandas as pd
from config import GOLD_PATH

def load_gold(path=GOLD_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=["date"])

def monthly_spend_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby([df["date"].dt.to_period("M"), "category"])["amount"]
          .sum()
          .reset_index()
          .rename(columns={"date": "month"})
    )

def total_spend_summary(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("category")["amount"]
          .sum()
          .reset_index()
          .sort_values("amount", ascending=False)
    )

def recurring_merchants(df: pd.DataFrame, min_transactions: int = 3) -> pd.DataFrame:
    """
    Merchants that appear at least `min_transactions` times.
    """
    grp = df.groupby("merchant").agg(
        n_txn=("merchant", "size"),
        total_spent=("amount", "sum")
    )
    return grp[grp["n_txn"] >= min_transactions].sort_values("n_txn", ascending=False)

def efficiency_score(df: pd.DataFrame) -> float:
    """
    Toy example: lower share of 'misc/shopping' -> higher score.
    You can refine this later.
    """
    total = df["amount"].sum()
    if total == 0:
        return 100.0

    bad_cats = ["shopping", "misc_net", "misc_pos"]
    mask = df["category"].str.lower().isin(bad_cats)
    bad_share = df.loc[mask, "amount"].sum() / total
    score = max(0, 100 * (1 - bad_share))
    return round(score, 2)