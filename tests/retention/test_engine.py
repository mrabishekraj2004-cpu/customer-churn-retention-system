from src.retention.engine import RetentionEngine


def make_customer() -> dict:
    return {
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


def test_high_risk_customer_gets_contract_migration() -> None:
    engine = RetentionEngine()

    result = engine.recommend(
        customer=make_customer(),
        churn_probability=0.90,
        operating_threshold=0.80,
    )

    assert result["retention_action_required"] is True
    assert result["action_type"] == "contract_migration"
    assert result["priority"] == "high"
    assert result["suggested_offer"] == (
        "Discount for switching to a one-year contract"
    )

    assert "Month-to-month contract" in result["risk_factors"]
    assert "Low customer tenure" in result["risk_factors"]
    assert "No technical support" in result["risk_factors"]


def test_customer_below_threshold_is_monitored() -> None:
    engine = RetentionEngine()

    result = engine.recommend(
        customer=make_customer(),
        churn_probability=0.50,
        operating_threshold=0.80,
    )

    assert result["retention_action_required"] is False
    assert result["action_type"] == "monitor"
    assert result["priority"] == "low"
    assert result["suggested_offer"] == "No immediate offer"


def test_support_offer_for_high_risk_customer_without_support() -> None:
    customer = make_customer()
    customer["Contract"] = "One year"
    customer["tenure"] = 24

    engine = RetentionEngine()

    result = engine.recommend(
        customer=customer,
        churn_probability=0.85,
        operating_threshold=0.80,
    )

    assert result["retention_action_required"] is True
    assert result["action_type"] == "support_offer"
    assert result["priority"] == "high"
    assert result["suggested_offer"] == (
        "Complimentary technical support trial"
    )


def test_fiber_customer_gets_service_review_when_other_rules_do_not_match() -> None:
    customer = make_customer()
    customer["Contract"] = "Two year"
    customer["tenure"] = 48
    customer["TechSupport"] = "Yes"

    engine = RetentionEngine()

    result = engine.recommend(
        customer=customer,
        churn_probability=0.85,
        operating_threshold=0.80,
    )

    assert result["retention_action_required"] is True
    assert result["action_type"] == "service_review"
    assert result["priority"] == "medium"
    assert result["suggested_offer"] == "Fiber service loyalty discount"