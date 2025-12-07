"""
model.py

Train a text classification model on the GOLD_ML dataset and save
a scikit-learn Pipeline (TF-IDF + LogisticRegression) to disk.

This model is later loaded by FinanceAI and used from the GUI.
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report
import joblib

from config import GOLD_ML_PATH, CATEGORY_MODEL_PATH


def load_training_data(path: str | None = None) -> pd.DataFrame:
    """Load the ML-ready dataset (description, amount, category)."""
    if path is None:
        path = GOLD_ML_PATH
    df = pd.read_csv(path)
    # Drop rows with missing description or category just in case
    df = df.dropna(subset=["description", "category"])
    return df


def train_model(df: pd.DataFrame) -> Pipeline:
    """
    Train a TF-IDF + LogisticRegression pipeline.

    Returns
    -------
    sklearn.pipeline.Pipeline
        Fitted pipeline ready to be saved/used.
    """
    X = df["description"].astype(str)
    y = df["category"].astype(str)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline = Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("clf", LogisticRegression(max_iter=1000, n_jobs=None)),
        ]
    )

    pipeline.fit(X_train, y_train)

    # Evaluation for the console
    y_pred = pipeline.predict(X_test)
    print(classification_report(y_test, y_pred))

    return pipeline


def main() -> None:
    df = load_training_data()
    model = train_model(df)

    # Save the full pipeline (vectorizer + classifier)
    CATEGORY_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, CATEGORY_MODEL_PATH)
    print(f"Model saved to {CATEGORY_MODEL_PATH}")


if __name__ == "__main__":
    main()