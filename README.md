# AI Personal Finance Copilot
 
Team Project – AI-powered Personal Finance Assistant
Team Members - Vansh Patel, Stuti Patel, Ratan Shanmugam Rajeshbabu

Github Link - https://github.com/vanshpatel9669/finance-ai-copilot-main
For the data download it with this - https://drive.google.com/file/d/1GyGIMOrhuddgUdCtwFRGmXBJXDlT03cD/view?usp=sharing

After downloading the data put that folder in the Project folder where all the python files are there in the structure shown below and run exactly as the steps mentioned below.
##  Project Overview

This project is an AI-powered personal finance copilot that:

- Ingests a large credit card transaction dataset (Kaggle)
- Cleans it through a **Bronze → Silver → Gold** data pipeline
- Trains a **scikit-learn** model to automatically classify transaction categories
- Provides analytics like monthly spending by category, recurring merchants, and an “efficiency score”
- Exposes functionality through:
  - A **Tkinter GUI** (desktop app)
  - An optional **Streamlit dashboard** (web-style app)

The codebase is organized into multiple Python modules, following a clean separation of concerns: data pipeline, analytics, model training, and GUI layer.


##  Project Structure

```text
Project_AAI/
├── app.py                  # Optional Streamlit dashboard
├── analytics.py            # Spending summaries and analytics helpers
├── config.py               # Central configuration (paths, model locations)
├── data_pipeline.py        # Bronze → Silver → Gold ETL pipeline
├── finance_ai.py           # FinanceAI class (model + analytics interface)
├── gui.py                  # Tkinter GUI using FinanceAI
├── model.py                # Model training (TF-IDF + Logistic Regression)
├── models/
│   └── category_model.joblib
├── data/
│   ├── raw/
│   │   └── credit_card_transactions.csv
│   ├── silver/
│   └── gold/
├── tests/
│   └── test_placeholder.py
├── requirements.txt
└── README.md

##  Environment Setup

This project was developed and tested with:

Python 3.11.x also supports version 3.12 or later and will run perfectly

Install dependencies:

pip install -r requirements.txt

 Data Pipeline (Bronze → Silver → Gold)

Place the raw Kaggle CSV in:

data/raw/credit_card_transactions.csv


Run the ETL pipeline:

python data_pipeline.py


This will create:

data/silver/credit_card_transactions_silver.csv

data/gold/transactions_gold.csv

data/gold/transactions_gold_ml.csv

 Train the Category Classification Model

Train the scikit-learn model (TF-IDF + Logistic Regression) and save it:

python model.py


This creates:

models/category_model.joblib


The model is later loaded by FinanceAI and used for predictions.

🧩 FinanceAI Class

finance_ai.py defines the FinanceAI class, which centralizes:

Loading the gold-level transaction data

Loading the trained model

Predicting categories for new transactions

Computing an overall efficiency score

The GUI and any future interfaces should use this class instead of working directly with the model or CSV files.

 Tkinter GUI 

Run the desktop GUI:

python gui.py


The GUI allows you to:

Enter a transaction description and predict its category

Compute and display an efficiency score based on spending

