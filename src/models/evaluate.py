import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_validate

from src.features.preprocess import (
    create_train_test_split,
    load_data,
    split_features_target,
)
from src.models.train import RANDOM_STATE, build_pipeline


def build_candidate_model():
    return LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )


def run_cross_validation(X: pd.DataFrame, y: pd.Series) -> None:
    pipeline = build_pipeline(build_candidate_model())

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    scoring = {
        "roc_auc": "roc_auc",
        "pr_auc": "average_precision",
        "precision": "precision",
        "recall": "recall",
        "f1": "f1",
    }

    scores = cross_validate(
        pipeline,
        X,
        y,
        cv=cv,
        scoring=scoring,
        n_jobs=-1,
    )

    print("\n5-fold cross-validation")

    for metric in scoring:
        values = scores[f"test_{metric}"]
        print(f"{metric:>10}: {values.mean():.4f} (+/- {values.std():.4f})")


def evaluate_thresholds(
    y_true: pd.Series,
    probabilities: np.ndarray,
) -> pd.DataFrame:
    thresholds = np.arange(0.20, 0.71, 0.05)

    rows = []

    for threshold in thresholds:
        predictions = (probabilities >= threshold).astype(int)

        rows.append(
            {
                "threshold": threshold,
                "precision": precision_score(
                    y_true,
                    predictions,
                    zero_division=0,
                ),
                "recall": recall_score(
                    y_true,
                    predictions,
                    zero_division=0,
                ),
                "f1": f1_score(
                    y_true,
                    predictions,
                    zero_division=0,
                ),
                "customers_flagged": int(predictions.sum()),
            }
        )

    return pd.DataFrame(rows)


def print_confusion_matrix(
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
) -> None:
    predictions = (probabilities >= threshold).astype(int)

    tn, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
    ).ravel()

    print(f"\nConfusion matrix at threshold {threshold:.2f}")
    print(f"True negatives:  {tn}")
    print(f"False positives: {fp}")
    print(f"False negatives: {fn}")
    print(f"True positives:  {tp}")


def main() -> None:
    df = load_data()
    X, y = split_features_target(df)

    run_cross_validation(X, y)

    X_train, X_test, y_train, y_test = create_train_test_split(
        X,
        y,
    )

    pipeline = build_pipeline(build_candidate_model())
    pipeline.fit(X_train, y_train)

    probabilities = pipeline.predict_proba(X_test)[:, 1]

    print("\nHoldout probability metrics")
    print(f"ROC-AUC: {roc_auc_score(y_test, probabilities):.4f}")
    print(f"PR-AUC: {average_precision_score(y_test, probabilities):.4f}")

    threshold_results = evaluate_thresholds(
        y_test,
        probabilities,
    )

    print("\nThreshold comparison")
    print(
        threshold_results.to_string(
            index=False,
            float_format=lambda value: f"{value:.4f}",
        )
    )

    best_f1_row = threshold_results.loc[threshold_results["f1"].idxmax()]

    best_threshold = float(best_f1_row["threshold"])

    print(f"\nBest threshold by F1: {best_threshold:.2f}")

    print_confusion_matrix(
        y_test,
        probabilities,
        best_threshold,
    )


if __name__ == "__main__":
    main()
