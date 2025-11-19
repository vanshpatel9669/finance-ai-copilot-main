# src/model.py
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from config import GOLD_ML_PATH, CATEGORY_MODEL_PATH

def load_training_data(path=GOLD_ML_PATH) -> pd.DataFrame:
    return pd.read_csv(path)

def build_pipeline() -> Pipeline:
    """Text (description) -> category classifier."""
    pipe = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=5000)),
        ("clf", LogisticRegression(max_iter=1000))
    ])
    return pipe

def train_and_save_model():
    df = load_training_data()

    X = df["description"]
    y = df["category"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipe = build_pipeline()
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)
    print(classification_report(y_test, y_pred))

    CATEGORY_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, CATEGORY_MODEL_PATH)
    print(f"Model saved to {CATEGORY_MODEL_PATH}")

def load_model() -> Pipeline:
    return joblib.load(CATEGORY_MODEL_PATH)

def predict_category(description: str, amount: float = 0.0) -> str:
    model = load_model()
    # For now, we only use description.
    return model.predict([description])[0]

if __name__ == "__main__":
    train_and_save_model()