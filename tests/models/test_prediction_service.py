import json
from pathlib import Path

import joblib
import pytest

from src.models.predict import PredictionService


class FakeModel:
    """Small serializable model used for PredictionService tests."""

    def predict_proba(self, customer):
        return [[0.25, 0.75]]


def create_test_metadata() -> dict:
    """Return metadata matching the PredictionService contract."""

    return {
        "model_name": "test_model",
        "model_version": "test-1.0.0",
        "operating_threshold": 0.8,
        "numeric_features": [
            "tenure",
            "MonthlyCharges",
        ],
        "categorical_features": [
            "Contract",
        ],
    }


def create_model_files(
    tmp_path: Path,
) -> tuple[Path, Path]:
    model_path = tmp_path / "model.joblib"
    metadata_path = tmp_path / "metadata.json"

    joblib.dump(
        FakeModel(),
        model_path,
    )

    metadata_path.write_text(
        json.dumps(create_test_metadata()),
        encoding="utf-8",
    )

    return model_path, metadata_path


def test_prediction_service_accepts_custom_model_paths(
    tmp_path: Path,
) -> None:
    model_path, metadata_path = create_model_files(tmp_path)

    service = PredictionService(
        model_path=model_path,
        metadata_path=metadata_path,
    )

    assert service.model is not None

    assert service.metadata["model_name"] == "test_model"
    assert service.metadata["model_version"] == "test-1.0.0"

    assert service.threshold == 0.8

    assert service.feature_names == [
        "tenure",
        "MonthlyCharges",
        "Contract",
    ]


def test_prediction_service_raises_for_missing_model(
    tmp_path: Path,
) -> None:
    model_path = tmp_path / "missing.joblib"
    metadata_path = tmp_path / "metadata.json"

    metadata_path.write_text(
        json.dumps(create_test_metadata()),
        encoding="utf-8",
    )

    with pytest.raises(
        FileNotFoundError,
        match="Model artifact not found",
    ):
        PredictionService(
            model_path=model_path,
            metadata_path=metadata_path,
        )


def test_prediction_service_raises_for_missing_metadata(
    tmp_path: Path,
) -> None:
    model_path = tmp_path / "model.joblib"
    metadata_path = tmp_path / "missing_metadata.json"

    joblib.dump(
        FakeModel(),
        model_path,
    )

    with pytest.raises(
        FileNotFoundError,
        match="Model metadata not found",
    ):
        PredictionService(
            model_path=model_path,
            metadata_path=metadata_path,
        )
