from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/raw/telco_customer_churn.csv")
TARGET_COLUMN = "Churn"


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Load the raw customer churn dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    return pd.read_csv(path)


def inspect_data(df: pd.DataFrame) -> None:
    """Print a quick overview of the dataset and obvious quality issues."""
    print("\nDataset shape")
    print(df.shape)

    print("\nData types")
    print(df.dtypes)

    print("\nMissing values")
    print(df.isna().sum().sort_values(ascending=False))

    print("\nDuplicate rows")
    print(df.duplicated().sum())

    print("\nUnique customers")
    print(df["customerID"].nunique())

    print("\nChurn distribution")
    print(df[TARGET_COLUMN].value_counts())

    print("\nChurn rate")
    print(df[TARGET_COLUMN].value_counts(normalize=True).mul(100).round(2))

    blank_total_charges = df["TotalCharges"].astype(str).str.strip().eq("").sum()

    print("\nBlank TotalCharges values")
    print(blank_total_charges)


def main() -> None:
    df = load_data()
    inspect_data(df)


if __name__ == "__main__":
    main()
