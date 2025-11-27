# tests/conftest.py
import pytest
from pathlib import Path
import pandas as pd

# Adjust these import paths if your files are located deeper
# (e.g., from src.transaction_manager import TransactionManager)
from transaction_manager import TransactionManager
from finance_ai import FinanceAI # Assuming collaborator's file is named this

# --- Fixtures for TransactionManager Testing ---

@pytest.fixture(scope='session')
def mock_gold_path():
    """
    Fixture to provide the absolute path to the mock gold dataset CSV
    located in the same tests/ directory.
    """
    # Path(__file__).parent refers to the current 'tests/' folder
    return Path(__file__).parent / "mock_gold_data.csv"

@pytest.fixture(scope='session')
def transaction_manager(mock_gold_path):
    """
    Fixture to instantiate and return the TransactionManager object,
    automatically loading the mock gold data.
    """
    return TransactionManager(gold_data_path=mock_gold_path)

# --- Fixtures for FinanceAI Testing ---

@pytest.fixture(scope='session')
def finance_ai_instance():
    """
    Fixture to instantiate the FinanceAI object for testing its methods
    like predict_category() and efficiency_score().
    """

    return FinanceAI()