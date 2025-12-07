# src/data_pipeline.py
import pandas as pd
from config import (
    RAW_TRANSACTIONS_PATH,
    SILVER_PATH,
    GOLD_PATH,
    GOLD_ML_PATH
)


def load_raw_data(path=RAW_TRANSACTIONS_PATH) -> pd.DataFrame:
    print("Loading from:", path)  # helpful debug print
    df_raw = pd.read_csv(path)
    return df_raw



def to_silver(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize the raw data.
    - Drop unused columns (if they exist)
    - Clean merchant names
    - Convert datetime
    """
    # Start with a copy
    df = df_raw.copy()

    # Drop Unnamed: 0 only if it exists
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # Rename key columns
    df = df.rename(columns={
        "trans_date_trans_time": "date",
        "merchant": "merchant",
        "category": "category",
        "amt": "amount",
    })

    # Convert to datetime and sort
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)

    # Clean merchant text
    df["merchant"] = (
        df["merchant"]
        .astype(str)
        .str.upper()
        .str.replace(r"[^A-Z0-9 ]", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Drop high-PII columns you don't need
    drop_cols = [
        "first", "last", "gender", "street", "city", "state", "zip",
        "lat", "long", "city_pop", "job", "dob"
    ]
    existing_drop = [c for c in drop_cols if c in df.columns]
    df = df.drop(columns=existing_drop)

    return df


def to_gold(df_silver: pd.DataFrame) -> pd.DataFrame:
    """
    Add features for ML and analytics.
    - add month/year
    - add type (Debit)
    - create description (merchant + category)
    - flag recurring merchants
    """
    df = df_silver.copy()

    df["month"] = df["date"].dt.to_period("M")
    df["year"] = df["date"].dt.year

    # In this dataset, all rows are charges, so mark as Debit
    df["type"] = "Debit"

    # Description used for NLP
    # Used only merchant text as description so it generalizes better
    df["description"] = df["merchant"].astype(str)

    # Simple recurring flag: same merchant & amount appears multiple times
    df["is_recurring"] = df.duplicated(subset=["merchant", "amount"], keep=False)

    return df


def run_full_pipeline():
    """Convenience function: bronze -> silver -> gold and save to disk."""
    df_raw = load_raw_data()
    df_silver = to_silver(df_raw)
    SILVER_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_silver.to_csv(SILVER_PATH, index=False)

    df_gold = to_gold(df_silver)
    GOLD_PATH.parent.mkdir(parents=True, exist_ok=True)
    df_gold.to_csv(GOLD_PATH, index=False)

    # Gold subset used for ML training
    df_ml = df_gold[["description", "amount", "category"]]
    df_ml.to_csv(GOLD_ML_PATH, index=False)


if __name__ == "__main__":
    run_full_pipeline()