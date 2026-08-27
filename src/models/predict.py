import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.config import settings


class PredictionService:
    def __init__(
        self,
        model_path: Path | None = None,
        metadata_path: Path | None = None,
    ) -> None:
        resolved_model_path = model_path or settings.model_path
        resolved_metadata_path = metadata_path or settings.model_metadata_path

        self.model = self._load_model(resolved_model_path)
        self.metadata = self._load_metadata(resolved_metadata_path)

        self.threshold = float(self.metadata["operating_threshold"])

        self.feature_names = (
            self.metadata["numeric_features"] + self.metadata["categorical_features"]
        )

    @staticmethod
    def _load_model(path: Path) -> Any:
        if not path.exists():
            raise FileNotFoundError(
                f"Model artifact not found: {path}. "
                "Run the production training pipeline first."
            )

        return joblib.load(path)

    @staticmethod
    def _load_metadata(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(
                f"Model metadata not found: {path}. "
                "Run the production training pipeline first."
            )

        with path.open(encoding="utf-8") as file:
            return json.load(file)

    def _validate_customer(
        self,
        customer: dict[str, Any],
    ) -> None:
        missing_features = set(self.feature_names) - set(customer)

        if missing_features:
            raise ValueError(
                f"Missing required customer features: {sorted(missing_features)}"
            )

    @staticmethod
    def _risk_level(probability: float) -> str:
        if probability >= 0.80:
            return "critical"

        if probability >= 0.60:
            return "high"

        if probability >= 0.40:
            return "medium"

        return "low"

    def predict(
        self,
        customer: dict[str, Any],
    ) -> dict[str, Any]:
        self._validate_customer(customer)

        customer_df = pd.DataFrame(
            [{feature: customer[feature] for feature in self.feature_names}]
        )

        probability = float(self.model.predict_proba(customer_df)[0, 1])

        return {
            "churn_probability": round(probability, 4),
            "risk_level": self._risk_level(probability),
            "retention_action_required": probability >= self.threshold,
            "operating_threshold": self.threshold,
            "model_version": self.metadata["model_version"],
        }
