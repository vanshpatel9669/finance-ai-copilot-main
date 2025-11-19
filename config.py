# config.py
from pathlib import Path

# Base directory = the folder where config.py lives
BASE_DIR = Path(__file__).resolve().parent

# Data folders
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
SILVER_DIR = DATA_DIR / "silver"
GOLD_DIR = DATA_DIR / "gold"
MODELS_DIR = BASE_DIR / "models"

# Raw Kaggle file (this is the important one)
RAW_TRANSACTIONS_PATH = RAW_DIR / "credit_card_transactions.csv"

# Cleaned outputs
SILVER_PATH = SILVER_DIR / "credit_card_transactions_silver.csv"
GOLD_PATH = GOLD_DIR / "transactions_gold.csv"
GOLD_ML_PATH = GOLD_DIR / "transactions_gold_ml.csv"

# Model path
CATEGORY_MODEL_PATH = MODELS_DIR / "category_model.joblib"
