"""
finance_ai.py

FinanceAI class: wrapper around the trained ML model and analytics.

For the GUI demo we use a HYBRID approach:
- Rule-based overrides for very common merchants/apps (Uber, Netflix, Shell,
  McDonalds, etc.) so predictions look realistic and intuitive.
- Otherwise, we fall back to the trained TF-IDF + LogisticRegression model.

This is a standard pattern in production systems: ML + business rules.
"""

from pathlib import Path
import joblib
import pandas as pd

from config import GOLD_PATH, CATEGORY_MODEL_PATH
from analytics import (
    load_gold,
    monthly_spend_by_category,
    total_spend_summary,
    recurring_merchants,
    efficiency_score,
)

# Human-friendly labels for categories (used in GUI)
CATEGORY_FRIENDLY = {
    "entertainment": "Entertainment",
    "food_dining": "Food & Dining",
    "gas_transport": "Gas / Transport",
    "grocery_net": "Groceries (Online)",
    "grocery_pos": "Groceries (In-Store)",
    "health_fitness": "Health & Fitness",
    "home": "Home & Utilities",
    "kids_pets": "Kids & Pets",
    "misc_net": "Miscellaneous (Online)",
    "misc_pos": "Miscellaneous (In-Store)",
    "personal_care": "Personal Care",
    "shopping_net": "Shopping (Online)",
    "shopping_pos": "Shopping (In-Store)",
    "travel": "Travel",
}


class FinanceAI:
    """
    High-level interface for the AI Personal Finance Copilot.

    - Loads gold-level transaction data
    - Loads the trained TF-IDF + Logistic Regression pipeline
    - Provides prediction and analytics helpers
    - Uses a small rule-based layer for very common merchants so the GUI
      behaves like a real banking app.
    """

    def __init__(
        self,
        data_path: str | Path = GOLD_PATH,
        model_path: str | Path = CATEGORY_MODEL_PATH,
    ) -> None:
        self.data_path = Path(data_path)
        self.model_path = Path(model_path)

        # Gold-level cleaned data
        self._df = load_gold(self.data_path)

        # Trained TF-IDF + LogisticRegression pipeline
        self._model = self._load_model()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_model(self):
        """Load the trained TF-IDF + LogisticRegression pipeline."""
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. "
                "Run `python model.py` first."
            )
        return joblib.load(self.model_path)

    def _rule_based_category(self, description: str) -> str | None:
        """
        Rule-based override for obvious merchants/apps.

        This makes the GUI demo behave like a real banking app even when the
        exact words were not present in the synthetic training data.
        """
        text = (description or "").lower()

        rules = {
            # transport / gas
            "uber": "gas_transport",
            "lyft": "gas_transport",
            "shell": "gas_transport",
            "exxon": "gas_transport",
            "chevron": "gas_transport",
            "bp gas": "gas_transport",

            # entertainment / subscriptions
            "netflix": "entertainment",
            "spotify": "entertainment",
            "hulu": "entertainment",
            "disney+": "entertainment",
            "prime video": "entertainment",
            "youtube premium": "entertainment",

            # food & dining
            "mcdonald": "food_dining",
            "mc donald": "food_dining",
            "starbucks": "food_dining",
            "burger king": "food_dining",
            "kfc": "food_dining",
            "dominos": "food_dining",
            "subway": "food_dining",

            # groceries / retail
            "walmart": "grocery_pos",
            "target": "grocery_pos",
            "costco": "grocery_pos",
            "whole foods": "grocery_pos",
            "trader joe": "grocery_pos",

            # travel
            "airbnb": "travel",
            "marriott": "travel",
            "delta": "travel",
            "united airlines": "travel",
            "american airlines": "travel",
        }

        for key, cat in rules.items():
            if key in text:
                return cat

        return None

    def pretty_category(self, label: str) -> str:
        """Return a human-friendly name for a raw category code."""
        return CATEGORY_FRIENDLY.get(label, label)

    # ------------------------------------------------------------------
    # Public data property
    # ------------------------------------------------------------------

    @property
    def df(self) -> pd.DataFrame:
        """Return a copy of the gold-level transaction DataFrame."""
        return self._df.copy()

    # ------------------------------------------------------------------
    # Prediction API
    # ------------------------------------------------------------------

    def predict_category(self, description: str) -> str:
        """
        Predict a category for a new transaction description.

        Returns ONLY the raw label (used by tests).
        """
        text = (description or "").strip()
        if not text:
            raise ValueError("Description must be a non-empty string.")

        # Try rule-based mapping first (for very common merchants)
        rb = self._rule_based_category(text)
        if rb is not None:
            return rb

        # Otherwise, use the ML model
        pred = self._model.predict([text])[0]
        return str(pred)

    def predict_with_proba(self, description: str, top_k: int = 3):
        """
        Return the main prediction plus top-k categories with probabilities.

        For GUI:
        - If rule-based layer fires → we return that label and mark source='rule'.
        - Otherwise → we return model's top prediction and source='model'.
        """
        text = (description or "").strip()
        if not text:
            raise ValueError("Description must be a non-empty string.")

        # 1) Rule-based override
        rb = self._rule_based_category(text)
        if rb is not None:
            return {
                "prediction": rb,
                "top_k": [(rb, 1.0)],
                "source": "rule",
            }

        # 2) Model path
        proba = self._model.predict_proba([text])[0]
        classes = self._model.classes_
        pairs = list(zip(classes, proba))
        pairs.sort(key=lambda x: x[1], reverse=True)
        top = pairs[:top_k]

        main_label = str(top[0][0])

        return {
            "prediction": main_label,
            "top_k": [(str(lbl), float(p)) for lbl, p in top],
            "source": "model",
        }

    # ------------------------------------------------------------------
    # Analytics helpers
    # ------------------------------------------------------------------

    def get_efficiency_score(self) -> float:
        """Compute the overall efficiency score (0–100)."""
        return efficiency_score(self._df)

    def get_category_efficiency(self, category: str) -> float:
        """
        Simple per-category impact score (0–100).

        Idea:
        - For 'non-essential' categories (shopping, misc, entertainment, food_dining),
          higher share of spending => lower score.
        - For more 'essential' categories, higher share => higher score.

        This is a heuristic just to make the GUI more interpretable.
        """
        if "amount" not in self._df.columns or "category" not in self._df.columns:
            return 50.0

        total = self._df["amount"].sum()
        if total == 0:
            return 100.0

        cat_total = self._df.loc[self._df["category"] == category, "amount"].sum()
        share = cat_total / total  # fraction of spending in this category

        bad_cats = {
            "shopping_net",
            "shopping_pos",
            "misc_net",
            "misc_pos",
            "entertainment",
            "food_dining",
        }

        if category in bad_cats:
            # More spending in 'bad' categories ⇒ lower score
            score = 100 * (1 - min(1.0, share * 5))
        else:
            # More spending in 'good/neutral' categories ⇒ higher score
            score = 100 * min(1.0, share * 5)

        return round(max(0.0, min(100.0, score)), 1)

    def get_monthly_summary(self, last_n_months: int = 6) -> pd.DataFrame:
        """Return monthly spending by category, limited to the last N months."""
        m = monthly_spend_by_category(self._df)
        m = m.sort_values("month")
        if last_n_months is not None and last_n_months > 0:
            # keep last N months × all categories
            m = m.tail(last_n_months * m["category"].nunique())
        return m

    def get_category_breakdown(self) -> pd.DataFrame:
        """Return total spend per category, descending."""
        return total_spend_summary(self._df)

    def get_recurring_merchants(self, min_transactions: int = 3) -> pd.DataFrame:
        """Return merchants that appear at least min_transactions times."""
        return recurring_merchants(self._df, min_transactions=min_transactions)

    def get_top_categories(self, n: int = 5) -> pd.DataFrame:
        """Return the top-n categories by total spend."""
        summary = total_spend_summary(self._df)
        return summary.head(n)

    def get_suspected_subscriptions(self) -> pd.DataFrame:
        """
        Heuristic: recurring merchants in entertainment / online categories
        are likely subscriptions (Netflix, Spotify, etc.).
        """
        rec = recurring_merchants(self._df, min_transactions=3).reset_index()

        if rec.empty:
            return pd.DataFrame(columns=["merchant", "total_spent"])

        df = self._df.merge(rec[["merchant"]], on="merchant", how="inner")
        mask = df["category"].isin(["entertainment", "shopping_net", "misc_net"])

        subs = (
            df.loc[mask]
            .groupby("merchant")["amount"]
            .sum()
            .reset_index()
            .rename(columns={"amount": "total_spent"})
            .sort_values("total_spent", ascending=False)
        )

        return subs