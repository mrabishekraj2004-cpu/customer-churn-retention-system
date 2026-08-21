from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix

from src.features.preprocess import (
    create_train_test_split,
    load_data,
    split_features_target,
)
from src.models.train import RANDOM_STATE, build_pipeline


@dataclass(frozen=True)
class RetentionEconomics:
    contact_cost: float = 10.0
    retention_offer_cost: float = 50.0
    retained_customer_value: float = 300.0
    offer_success_rate: float = 0.30

    @property
    def campaign_cost(self) -> float:
        return self.contact_cost + self.retention_offer_cost


def build_model():
    return LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )


def calculate_business_metrics(
    y_true: pd.Series,
    probabilities: np.ndarray,
    threshold: float,
    economics: RetentionEconomics,
) -> dict[str, float]:
    predictions = (probabilities >= threshold).astype(int)

    _, fp, fn, tp = confusion_matrix(
        y_true,
        predictions,
    ).ravel()

    customers_targeted = tp + fp

    campaign_cost = customers_targeted * economics.campaign_cost

    expected_saved_customers = tp * economics.offer_success_rate

    expected_retained_value = (
        expected_saved_customers * economics.retained_customer_value
    )

    expected_net_value = expected_retained_value - campaign_cost

    return {
        "threshold": threshold,
        "targeted": customers_targeted,
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "expected_saved": expected_saved_customers,
        "campaign_cost": campaign_cost,
        "expected_value": expected_retained_value,
        "net_value": expected_net_value,
    }


def evaluate_thresholds(
    y_true: pd.Series,
    probabilities: np.ndarray,
    economics: RetentionEconomics,
) -> pd.DataFrame:
    thresholds = np.arange(0.20, 0.81, 0.05)

    results = [
        calculate_business_metrics(
            y_true,
            probabilities,
            threshold,
            economics,
        )
        for threshold in thresholds
    ]

    return pd.DataFrame(results)


def main() -> None:
    df = load_data()
    X, y = split_features_target(df)

    X_train, X_test, y_train, y_test = create_train_test_split(
        X,
        y,
    )

    pipeline = build_pipeline(build_model())
    pipeline.fit(X_train, y_train)

    probabilities = pipeline.predict_proba(X_test)[:, 1]

    economics = RetentionEconomics()

    results = evaluate_thresholds(
        y_test,
        probabilities,
        economics,
    )

    print("\nPrototype retention assumptions")
    print(f"Contact cost: ${economics.contact_cost:.2f}")
    print(f"Offer cost: ${economics.retention_offer_cost:.2f}")
    print(f"Retained customer value: ${economics.retained_customer_value:.2f}")
    print(f"Expected offer success rate: {economics.offer_success_rate:.0%}")

    print("\nBusiness value by threshold")

    print(
        results.to_string(
            index=False,
            formatters={
                "threshold": "{:.2f}".format,
                "expected_saved": "{:.1f}".format,
                "campaign_cost": "${:,.2f}".format,
                "expected_value": "${:,.2f}".format,
                "net_value": "${:,.2f}".format,
            },
        )
    )

    best_result = results.loc[results["net_value"].idxmax()]

    print("\nBest threshold under these assumptions")
    print(f"Threshold: {best_result['threshold']:.2f}")
    print(f"Customers targeted: {int(best_result['targeted'])}")
    print(f"Expected net value: ${best_result['net_value']:,.2f}")


if __name__ == "__main__":
    main()
