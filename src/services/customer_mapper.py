from typing import Any


def to_database_customer(
    customer: dict[str, Any],
) -> dict[str, Any]:
    """Convert API customer fields to database column names."""
    return {
        "gender": customer["gender"],
        "senior_citizen": customer["SeniorCitizen"],
        "partner": customer["Partner"],
        "dependents": customer["Dependents"],
        "tenure": customer["tenure"],
        "phone_service": customer["PhoneService"],
        "multiple_lines": customer["MultipleLines"],
        "internet_service": customer["InternetService"],
        "online_security": customer["OnlineSecurity"],
        "online_backup": customer["OnlineBackup"],
        "device_protection": customer["DeviceProtection"],
        "tech_support": customer["TechSupport"],
        "streaming_tv": customer["StreamingTV"],
        "streaming_movies": customer["StreamingMovies"],
        "contract": customer["Contract"],
        "paperless_billing": customer["PaperlessBilling"],
        "payment_method": customer["PaymentMethod"],
        "monthly_charges": customer["MonthlyCharges"],
        "total_charges": customer["TotalCharges"],
    }


def to_model_features(
    customer: dict[str, Any],
) -> dict[str, Any]:
    """Remove application-only fields before ML prediction."""
    return {key: value for key, value in customer.items() if key != "customer_id"}
