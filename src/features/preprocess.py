from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DATA_PATH = Path("data/processed/telco_customer_churn.csv")

TARGET_COLUMN = "Churn"
ID_COLUMN = "customerID"

NUMERIC_FEATURES = [
    "SeniorCitizen",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
]

CATEGORICAL_FEATURES = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
]


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the cleaned customer dataset."""
    if not path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {path}. Run the cleaning pipeline first."
        )

    return pd.read_csv(path)


def split_features_target(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.Series]:
    """Separate model features from the churn target."""
    feature_columns = NUMERIC_FEATURES + CATEGORICAL_FEATURES

    X = df[feature_columns].copy()
    y = df[TARGET_COLUMN].map({"No": 0, "Yes": 1})

    if y.isna().any():
        raise ValueError("Unexpected values found in the churn target.")

    return X, y.astype(int)


def build_preprocessor() -> ColumnTransformer:
    """Create preprocessing steps for numeric and categorical features."""
    numeric_transformer = StandardScaler()

    categorical_transformer = OneHotEncoder(
        handle_unknown="ignore",
    )

    return ColumnTransformer(
        transformers=[
            (
                "numeric",
                numeric_transformer,
                NUMERIC_FEATURES,
            ),
            (
                "categorical",
                categorical_transformer,
                CATEGORICAL_FEATURES,
            ),
        ]
    )


def create_train_test_split(
    X: pd.DataFrame,
    y: pd.Series,
    test_size: float = 0.2,
    random_state: int = 42,
) -> tuple[
    pd.DataFrame,
    pd.DataFrame,
    pd.Series,
    pd.Series,
]:
    """Create a reproducible stratified train/test split."""
    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )


def main() -> None:
    df = load_data()

    X, y = split_features_target(df)

    X_train, X_test, y_train, y_test = create_train_test_split(X, y)

    preprocessor = build_preprocessor()
    preprocessor.fit(X_train)

    print(f"Training rows: {len(X_train):,}")
    print(f"Test rows: {len(X_test):,}")

    print(f"Training churn rate: {y_train.mean():.2%}")
    print(f"Test churn rate: {y_test.mean():.2%}")

    print(f"Model input features: {X.shape[1]}")
    print(f"Numeric features: {len(NUMERIC_FEATURES)}")
    print(f"Categorical features: {len(CATEGORICAL_FEATURES)}")

    transformed_train = preprocessor.transform(X_train)

    print(f"Features after encoding: {transformed_train.shape[1]}")


if __name__ == "__main__":
    main()
