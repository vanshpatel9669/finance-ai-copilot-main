"""
tests/test_placeholder.py

Starter pytest file for the AI Personal Finance Copilot project.
As the project evolves, more targeted tests should be added for:

- FinanceAI.predict_category
- FinanceAI.get_efficiency_score
- Analytics functions (monthly_spend_by_category, etc.)
- Data pipeline functions
"""
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from finance_ai import FinanceAI



def test_finance_ai_initialization():
    """
    Basic smoke test to ensure that FinanceAI can be instantiated
    without raising an exception. This indirectly verifies that:

    - The gold CSV file is reachable via config.GOLD_PATH
    - The trained model file exists at config.CATEGORY_MODEL_PATH
    """
    engine = FinanceAI()
    assert engine is not None


def test_efficiency_score_range():
    """
    Verify that the efficiency score is always between 0 and 100.
    """
    engine = FinanceAI()
    score = engine.get_efficiency_score()
    assert 0.0 <= score <= 100.0

def test_prediction_runs():
    """
    Ensures the model can generate a prediction for a valid description,
    and that it returns a string.
    """
    engine = FinanceAI()
    pred = engine.predict_category("NETFLIX subscription")
    assert isinstance(pred, str)


def test_data_loaded():
    """
    Ensures that the gold dataset is successfully loaded and not empty.
    """
    engine = FinanceAI()
    df = engine.df
    assert not df.empty
    assert "amount" in df.columns


def test_efficiency_score_type():
    """
    Ensures that efficiency score returned is a float.
    """
    engine = FinanceAI()
    score = engine.get_efficiency_score()
    assert isinstance(score, float)