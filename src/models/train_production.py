import json
from datetime import UTC, datetime
from pathlib import Path

import joblib
from sklearn.linear_model import LogisticRegression

from src.features.preprocess import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    load_data,
    split_features_target,
)
from src.models.train import RANDOM_STATE, build_pipeline

MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "churn_pipeline.joblib"
METADATA_PATH = MODEL_DIR / "churn_pipeline_metadata.json"

MODEL_VERSION = "1.0.0"

# Selected from the prototype business-value analysis.
# This is a configurable operating policy, not an intrinsic model threshold.
OPERATING_THRESHOLD = 0.80


def build_production_model():
    classifier = LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )

    return build_pipeline(classifier)


def build_metadata(training_rows: int) -> dict:
    return {
        "model_name": "customer_churn_logistic_regression",
        "model_version": MODEL_VERSION,
        "trained_at_utc": datetime.now(UTC).isoformat(),
        "training_rows": training_rows,
        "target": "Churn",
        "positive_class": "Yes",
        "operating_threshold": OPERATING_THRESHOLD,
        "numeric_features": NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
    }


def save_model(model, metadata: dict) -> None:
    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, MODEL_PATH)

    with METADATA_PATH.open("w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)


def main() -> None:
    df = load_data()
    X, y = split_features_target(df)

    model = build_production_model()
    model.fit(X, y)

    metadata = build_metadata(training_rows=len(X))

    save_model(model, metadata)

    print(f"Production model trained on {len(X):,} customers.")
    print(f"Model saved to: {MODEL_PATH}")
    print(f"Metadata saved to: {METADATA_PATH}")
    print(f"Model version: {MODEL_VERSION}")
    print(f"Operating threshold: {OPERATING_THRESHOLD:.2f}")


if __name__ == "__main__":
    main()
