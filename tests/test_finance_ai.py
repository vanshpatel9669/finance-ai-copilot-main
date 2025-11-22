# tests/test_finance_ai.py
import pytest


# No need for the FinanceAI import, as the fixture handles it

# 4. Test predict_category()
def test_predict_category(finance_ai_instance):
    """
    Tests the ML model's ability to predict a category based on transaction description.
    (Assumes a simple mapping or a trained model loads successfully).
    """
    # Case 1: Test with a description known to map to 'Food'
    prediction_food = finance_ai_instance.predict_category("Whole Foods Market")
    assert prediction_food == "Food"

    # Case 2: Test with a description known to map to 'Travel'
    prediction_travel = finance_ai_instance.predict_category("Delta Airlines")
    assert prediction_travel == "Travel"


# 5. Test efficiency_score()
def test_efficiency_score(finance_ai_instance):
    """
    Tests the calculation of the financial efficiency score for accuracy.
    (Assumes the function accepts total income and total expenses).
    """
    # Test Case: High efficiency (low expenses relative to income)
    # Income = 5000, Expenses = 1000
    # Score depends on collaborator's formula, but let's assume it's a simple ratio test.
    # If formula is (Income - Expenses) / Income * 100 --> (4000/5000) * 100 = 80.0
    score_high = finance_ai_instance.efficiency_score(total_income=5000, total_expenses=1000)

    # Use pytest.approx for floating point comparisons to avoid errors
    assert score_high == pytest.approx(80.0)

    # Test Case: Low efficiency (expenses closer to income)
    # Income = 5000, Expenses = 4500
    # Score: (500/5000) * 100 = 10.0
    score_low = finance_ai_instance.efficiency_score(total_income=5000, total_expenses=4500)
    assert score_low == pytest.approx(10.0)