from pathlib import Path

import pandas as pd

DATA_PATH = Path("data/processed/telco_customer_churn.csv")

SEGMENT_COLUMNS = [
    "Contract",
    "InternetService",
    "PaymentMethod",
    "TechSupport",
    "OnlineSecurity",
    "PaperlessBilling",
]


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Processed dataset not found: {path}. Run the cleaning pipeline first."
        )

    return pd.read_csv(path)


def add_analysis_fields(df: pd.DataFrame) -> pd.DataFrame:
    analyzed = df.copy()

    analyzed["churned"] = analyzed["Churn"].eq("Yes").astype(int)

    analyzed["tenure_group"] = pd.cut(
        analyzed["tenure"],
        bins=[-1, 12, 24, 48, 60, float("inf")],
        labels=["0-12", "13-24", "25-48", "49-60", "61+"],
    )

    return analyzed


def summarize_overall(df: pd.DataFrame) -> None:
    customer_count = len(df)
    churned_customers = int(df["churned"].sum())
    churn_rate = df["churned"].mean() * 100

    print("\nOverall churn")
    print(f"Customers: {customer_count:,}")
    print(f"Churned: {churned_customers:,}")
    print(f"Churn rate: {churn_rate:.2f}%")


def churn_by_segment(df: pd.DataFrame, column: str) -> pd.DataFrame:
    summary = (
        df.groupby(column, observed=True)
        .agg(
            customers=("customerID", "count"),
            churned=("churned", "sum"),
            churn_rate=("churned", "mean"),
        )
        .reset_index()
    )

    summary["churn_rate"] = (summary["churn_rate"] * 100).round(2)

    return summary.sort_values("churn_rate", ascending=False)


def summarize_numeric_features(df: pd.DataFrame) -> None:
    summary = (
        df.groupby("Churn")[["tenure", "MonthlyCharges", "TotalCharges"]]
        .mean()
        .round(2)
    )

    print("\nAverage customer values by churn status")
    print(summary.to_string())


def run_segment_analysis(df: pd.DataFrame) -> None:
    columns = [*SEGMENT_COLUMNS, "tenure_group"]

    for column in columns:
        print(f"\nChurn by {column}")
        print(churn_by_segment(df, column).to_string(index=False))


def main() -> None:
    df = load_data()
    df = add_analysis_fields(df)

    summarize_overall(df)
    summarize_numeric_features(df)
    run_segment_analysis(df)


if __name__ == "__main__":
    main()
