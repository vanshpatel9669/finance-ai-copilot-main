# transaction_manager.py
import pandas as pd
from datetime import datetime
import os


class TransactionManager:
    """
    Manages loading, filtering, and summarizing financial transaction data 
    from the 'gold' dataset.

    Assumes the gold dataset has columns: 
    'Date' (must be convertible to datetime), 'Amount' (negative for spending), 
    and 'Category' (for grouping/filtering).
    """

    def __init__(self, gold_data_path):
        self.gold_data_path = gold_data_path
        self.df = self._load_data()
        self._preprocess_data()

    def _load_data(self):
        """Loads the gold dataset into a pandas DataFrame."""
        if not os.path.exists(self.gold_data_path):
            raise FileNotFoundError(f"Gold dataset not found at: {self.gold_data_path}")

        # We assume the gold dataset is a CSV based on standard pipelines
        return pd.read_csv(self.gold_data_path)

    def _preprocess_data(self):
        """Converts the 'Date' column to datetime objects."""
        if 'Date' in self.df.columns:
            # Errors='coerce' will turn non-date values into NaT (Not a Time)
            self.df['Date'] = pd.to_datetime(self.df['Date'], errors='coerce')
            # Remove any rows where the date failed to parse
            self.df.dropna(subset=['Date'], inplace=True)
        else:
            print("Warning: 'Date' column not found for preprocessing.")

    # --- Filtering Methods ---

    def filter_by_date_range(self, start_date_str, end_date_str):
        """
        Filters transactions between two dates (inclusive).

        Args:
            start_date_str (str): The start date (e.g., 'YYYY-MM-DD').
            end_date_str (str): The end date (e.g., 'YYYY-MM-DD').

        Returns:
            pd.DataFrame: A DataFrame containing transactions within the range.
        """
        try:
            start_date = pd.to_datetime(start_date_str)
            end_date = pd.to_datetime(end_date_str)
        except ValueError:
            raise ValueError("Invalid date format provided. Use 'YYYY-MM-DD'.")

        filtered_df = self.df[
            (self.df['Date'] >= start_date) &
            (self.df['Date'] <= end_date)
            ].copy()

        return filtered_df

    def filter_by_month(self, year, month):
        """
        Filters transactions for a specific month and year.

        Args:
            year (int): The year (e.g., 2024).
            month (int): The month (1-12).

        Returns:
            pd.DataFrame: A DataFrame containing transactions for the specified month.
        """
        if not all(col in self.df.columns for col in ['Date']):
            raise KeyError("DataFrame is missing the required 'Date' column.")

        filtered_df = self.df[
            (self.df['Date'].dt.year == year) &
            (self.df['Date'].dt.month == month)
            ].copy()

        return filtered_df

    def filter_by_category(self, categories: list, df=None):
        """
        Filters transactions by a list of categories.

        Args:
            categories (list): A list of category names (strings) to include.
            df (pd.DataFrame, optional): The source DataFrame to filter. 
                                         Defaults to self.df if None.

        Returns:
            pd.DataFrame: A DataFrame containing only the specified categories.
        """
        source_df = df if df is not None else self.df

        if not all(col in source_df.columns for col in ['Category']):
            raise KeyError("DataFrame is missing the required 'Category' column.")

        filtered_df = source_df[
            source_df['Category'].isin(categories)
        ].copy()

        return filtered_df

    # --- Summary Methods ---

    def get_monthly_spend(self, df=None):
        """
        Calculates the total spend for each month present in the DataFrame.
        Spend is defined as negative values in the 'Amount' column.

        Args:
            df (pd.DataFrame, optional): The source DataFrame. Defaults to self.df.

        Returns:
            pd.DataFrame: A summary table with 'YearMonth' and 'Total_Spend'.
        """
        source_df = df if df is not None else self.df

        if not all(col in source_df.columns for col in ['Date', 'Amount']):
            raise KeyError("DataFrame is missing the required 'Date' or 'Amount' column.")

        # 1. Add a 'YearMonth' column for grouping
        monthly_spend_df = source_df.copy()
        monthly_spend_df['YearMonth'] = monthly_spend_df['Date'].dt.to_period('M')

        # 2. Filter only for spending (negative amounts)
        spend = monthly_spend_df[monthly_spend_df['Amount'] < 0]

        # 3. Calculate the absolute sum of negative amounts for each month
        summary = spend.groupby('YearMonth')['Amount'].sum().abs().reset_index()
        summary.rename(columns={'Amount': 'Total_Spend'}, inplace=True)

        return summary

    def get_top_categories(self, n=5, df=None):
        """
        Identifies the top N categories by total spend.

        Args:
            n (int): The number of top categories to return. Defaults to 5.
            df (pd.DataFrame, optional): The source DataFrame. Defaults to self.df.

        Returns:
            pd.DataFrame: A summary table with 'Category' and 'Total_Spend'.
        """
        source_df = df if df is not None else self.df

        if not all(col in source_df.columns for col in ['Category', 'Amount']):
            raise KeyError("DataFrame is missing the required 'Category' or 'Amount' column.")

        # 1. Filter for spending and calculate absolute amount
        spend_df = source_df[source_df['Amount'] < 0].copy()
        spend_df['Abs_Amount'] = spend_df['Amount'].abs()

        # 2. Group by the Category column
        category_spend = spend_df.groupby('Category')['Abs_Amount'].sum()

        # 3. Get the top N and format output
        top_categories = category_spend.nlargest(n).reset_index()
        top_categories.rename(columns={'Abs_Amount': 'Total_Spend'}, inplace=True)

        return top_categories