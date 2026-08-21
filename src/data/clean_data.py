from pathlib import Path

import pandas as pd

RAW_DATA_PATH = Path("data/raw/telco_customer_churn.csv")
PROCESSED_DATA_PATH = Path("data/processed/telco_customer_churn.csv")

REQUIRED_COLUMNS = {
    "customerID",
    "tenure",
    "MonthlyCharges",
    "TotalCharges",
    "Churn",
}

VALID_CHURN_VALUES = {"Yes", "No"}


def load_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load customer data from a CSV file."""
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    return pd.read_csv(path)


def validate_data(df: pd.DataFrame) -> None:
    """Check the raw data for problems that should stop processing."""
    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    if df.empty:
        raise ValueError("Dataset is empty.")

    if df["customerID"].isna().any():
        raise ValueError("Missing customer IDs found.")

    if df["customerID"].duplicated().any():
        raise ValueError("Duplicate customer IDs found.")

    invalid_churn_values = set(df["Churn"].dropna().unique()) - VALID_CHURN_VALUES

    if invalid_churn_values:
        raise ValueError(f"Unexpected Churn values: {sorted(invalid_churn_values)}")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean fields needed by the churn model."""
    cleaned = df.copy()

    cleaned["TotalCharges"] = pd.to_numeric(
        cleaned["TotalCharges"].str.strip(),
        errors="coerce",
    )

    missing_total_charges = cleaned["TotalCharges"].isna()

    cleaned.loc[missing_total_charges, "TotalCharges"] = (
        cleaned.loc[missing_total_charges, "MonthlyCharges"]
        * cleaned.loc[missing_total_charges, "tenure"]
    )

    return cleaned


def save_data(
    df: pd.DataFrame,
    path: Path = PROCESSED_DATA_PATH,
) -> None:
    """Save cleaned customer data."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> None:
    df = load_data()

    validate_data(df)
    cleaned = clean_data(df)
    save_data(cleaned)

    print(f"Processed {len(cleaned):,} customer records.")
    print(f"Saved cleaned data to: {PROCESSED_DATA_PATH}")
    print(f"Missing values remaining: {cleaned.isna().sum().sum()}")


if __name__ == "__main__":
    main()
