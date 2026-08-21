from dataclasses import dataclass

import pandas as pd
from sklearn.base import ClassifierMixin
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline

from src.features.preprocess import (
    build_preprocessor,
    create_train_test_split,
    load_data,
    split_features_target,
)

RANDOM_STATE = 42


@dataclass
class ModelResult:
    name: str
    roc_auc: float
    pr_auc: float
    precision: float
    recall: float
    f1: float


def build_models() -> dict[str, ClassifierMixin]:
    return {
        "Logistic Regression": LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=RANDOM_STATE,
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1,
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            random_state=RANDOM_STATE,
        ),
    }


def build_pipeline(model: ClassifierMixin) -> Pipeline:
    return Pipeline(
        steps=[
            ("preprocessor", build_preprocessor()),
            ("classifier", model),
        ]
    )


def evaluate_model(
    name: str,
    pipeline: Pipeline,
    X_test: pd.DataFrame,
    y_test: pd.Series,
) -> ModelResult:
    predictions = pipeline.predict(X_test)
    probabilities = pipeline.predict_proba(X_test)[:, 1]

    return ModelResult(
        name=name,
        roc_auc=roc_auc_score(y_test, probabilities),
        pr_auc=average_precision_score(y_test, probabilities),
        precision=precision_score(y_test, predictions),
        recall=recall_score(y_test, predictions),
        f1=f1_score(y_test, predictions),
    )


def main() -> None:
    df = load_data()
    X, y = split_features_target(df)

    X_train, X_test, y_train, y_test = create_train_test_split(X, y)

    results: list[ModelResult] = []

    for name, model in build_models().items():
        pipeline = build_pipeline(model)
        pipeline.fit(X_train, y_train)

        result = evaluate_model(
            name,
            pipeline,
            X_test,
            y_test,
        )
        results.append(result)

    results_df = pd.DataFrame([result.__dict__ for result in results]).sort_values(
        "pr_auc", ascending=False
    )

    print("\nBaseline model comparison")
    print(results_df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))


if __name__ == "__main__":
    main()
