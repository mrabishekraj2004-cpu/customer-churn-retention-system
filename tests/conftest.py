from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from api.main import app
from api.routes.prediction import get_prediction_service
from src.database import models  # noqa: F401
from src.database.session import Base, get_db


class FakePredictionService:
    """Fake predictor used by API tests so CI does not need model artifacts."""

    def predict(self, customer: dict) -> dict:
        monthly_charges = float(customer["MonthlyCharges"])
        tenure = int(customer["tenure"])
        contract = customer["Contract"]

        churn_probability = 0.85

        if contract == "Two year":
            churn_probability -= 0.35

        if tenure >= 24:
            churn_probability -= 0.15

        if monthly_charges < 50:
            churn_probability -= 0.10

        churn_probability = max(
            0.0,
            min(churn_probability, 1.0),
        )

        if churn_probability >= 0.80:
            risk_level = "critical"
        elif churn_probability >= 0.60:
            risk_level = "high"
        elif churn_probability >= 0.30:
            risk_level = "medium"
        else:
            risk_level = "low"

        return {
            "churn_probability": churn_probability,
            "risk_level": risk_level,
            "retention_action_required": churn_probability >= 0.80,
            "operating_threshold": 0.80,
            "model_version": "1.0.0",
        }


@pytest.fixture
def db_session(tmp_path) -> Generator[Session, None, None]:
    database_path = tmp_path / "api_test.db"

    engine = create_engine(
        f"sqlite:///{database_path}",
        connect_args={"check_same_thread": False},
    )

    testing_session = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    Base.metadata.create_all(bind=engine)

    session = testing_session()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(
    db_session: Session,
) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    def override_prediction_service() -> FakePredictionService:
        return FakePredictionService()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_prediction_service] = override_prediction_service

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def customer_payload() -> dict:
    return {
        "customer_id": "TEST-API-0001",
        "gender": "Male",
        "SeniorCitizen": 0,
        "Partner": "No",
        "Dependents": "No",
        "tenure": 5,
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
        "MonthlyCharges": 89.50,
        "TotalCharges": 447.50,
    }
