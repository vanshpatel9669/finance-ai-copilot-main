# tests/test_transaction_manager.py
import pytest
import pandas as pd


# No need for imports like TransactionManager here, as fixtures handle it

# 1. Test Gold Dataset Loading
def test_gold_dataset_loading(transaction_manager):
    """
    Ensures the gold dataset is loaded, is not empty, and the 'Date'
    column is correctly converted to datetime objects.
    """
    df = transaction_manager.df

    # Check 1: DataFrame should not be empty
    assert not df.empty

    # Check 2: Ensure the correct number of rows from the mock data (8 rows)
    assert df.shape[0] == 8

    # Check 3: Ensure the Date column is recognized as a datetime type
    assert pd.api.types.is_datetime64_any_dtype(df['Date'])


# 2. Test TransactionManager.filter_by_month()
def test_transaction_manager_filter_by_month(transaction_manager):
    """
    Ensures filtering for a specific month (March 2024) returns the correct number of rows.
    """
    # Based on mock_gold_data.csv, March 2024 has 3 transactions.
    march_transactions = transaction_manager.filter_by_month(year=2024, month=3)

    # Check 1: Should have 3 transactions
    assert march_transactions.shape[0] == 3

    # Check 2: All dates must fall within March (month=3)
    assert all(march_transactions['Date'].dt.month == 3)


# 3. Test Top Categories / Monthly Spend By Category
def test_monthly_spend_by_category(transaction_manager):
    """
    Tests the summary calculation for total spend by category (using get_top_categories).
    """
    # Expected spending based on mock_gold_data.csv:
    # Food: 50.00 (Mar) + 25.00 (Apr) = 75.00
    # Bills: 120.00 (Mar) + 150.00 (May) = 270.00
    # Travel: 300.00 (Apr) = 300.00

    summary = transaction_manager.get_top_categories(n=5)

    # Check 1: The 'Travel' category should have the highest spend (300.00)
    travel_spend = summary[summary['Category'] == 'Travel']['Total_Spend'].iloc[0]
    assert travel_spend == 300.00

    # Check 2: The 'Bills' spend is correct (270.00)
    bills_spend = summary[summary['Category'] == 'Bills']['Total_Spend'].iloc[0]
    assert bills_spend == 270.00