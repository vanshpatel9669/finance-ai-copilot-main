"""
finance_ai.py

FinanceAI class: Thin wrapper around the trained ML model and
analytics functions. This class is used by the GUI to:

- Load the gold-level transaction dataset
- Load the trained scikit-learn model
- Predict the category for a new transaction description
- Compute a simple spending efficiency score
"""

from pathlib import Path
import joblib
import pandas as pd

from config import GOLD_PATH, CATEGORY_MODEL_PATH
from analytics import load_gold, efficiency_score


class FinanceAI:
    """
    High-level interface for the AI Personal Finance Copilot.

    This class centralizes:
    - Access to the cleaned (gold) transaction data
    - Access to the trained category classification model
    - Utility methods used by the GUI layer
    """

    def __init__(
        self,
        data_path: Path | str = GOLD_PATH,
        model_path: Path | str = CATEGORY_MODEL_PATH,
    ) -> None:
        """
        Initialize the FinanceAI engine.

        Parameters
        ----------
        data_path : str or Path
            Path to the gold-level transaction CSV.
        model_path : str or Path
            Path to the saved scikit-learn model (joblib).
        """
        self.data_path = Path(data_path)
        self.model_path = Path(model_path)

        # Load data and model at startup so the GUI can call quickly.
        self._df = load_gold(self.data_path)
        self._model = self._load_model()

    def _load_model(self):
        """
        Internal helper to load the trained model from disk.

        Returns
        -------
        sklearn.pipeline.Pipeline
            Trained TF-IDF + LogisticRegression pipeline.
        """
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at {self.model_path}. "
                "Make sure you ran `python model.py` first."
            )
        return joblib.load(self.model_path)

    @property
    def df(self) -> pd.DataFrame:
        """
        Expose the underlying transactions DataFrame (read-only).
        """
        return self._df.copy()

    def predict_category(self, description: str) -> str:
        """
        Predict the spending category for a new transaction description.

        Parameters
        ----------
        description : str
            Free-text description of the transaction (e.g. 'NETFLIX.COM').

        Returns
        -------
        str
            Predicted category label.
        """
        if not description or not description.strip():
            raise ValueError("Description must be a non-empty string.")

        pred = self._model.predict([description.strip()])[0]
        return str(pred)

    def get_efficiency_score(self) -> float:
        """
        Compute the current efficiency score for the loaded dataset.

        Returns
        -------
        float
            Efficiency score in [0, 100].
        """
        return efficiency_score(self._df)