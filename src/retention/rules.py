from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetentionRecommendation:
    action_type: str
    suggested_offer: str
    priority: str
    reason: str


def get_risk_factors(
    customer: dict[str, Any],
) -> list[str]:
    """Identify explainable customer characteristics linked to churn risk."""
    risk_factors: list[str] = []

    if customer["Contract"] == "Month-to-month":
        risk_factors.append("Month-to-month contract")

    if customer["InternetService"] == "Fiber optic":
        risk_factors.append("Fiber optic service")

    if customer["TechSupport"] == "No":
        risk_factors.append("No technical support")

    if customer["OnlineSecurity"] == "No":
        risk_factors.append("No online security")

    if customer["PaymentMethod"] == "Electronic check":
        risk_factors.append("Electronic check payment")

    if customer["PaperlessBilling"] == "Yes":
        risk_factors.append("Paperless billing")

    if customer["tenure"] <= 12:
        risk_factors.append("Low customer tenure")

    return risk_factors


def get_retention_recommendation(
    customer: dict[str, Any],
    churn_probability: float,
    operating_threshold: float,
) -> RetentionRecommendation:
    """Generate an explainable retention recommendation."""

    if churn_probability < operating_threshold:
        return RetentionRecommendation(
            action_type="monitor",
            suggested_offer="No immediate offer",
            priority="low",
            reason="Customer is below the retention intervention threshold.",
        )

    if customer["Contract"] == "Month-to-month" and customer["tenure"] <= 12:
        return RetentionRecommendation(
            action_type="contract_migration",
            suggested_offer="Discount for switching to a one-year contract",
            priority="high",
            reason=(
                "Short-tenure customer on a month-to-month contract "
                "with elevated churn risk."
            ),
        )

    if customer["TechSupport"] == "No":
        return RetentionRecommendation(
            action_type="support_offer",
            suggested_offer="Complimentary technical support trial",
            priority="high",
            reason=("High-risk customer currently has no technical support."),
        )

    if customer["InternetService"] == "Fiber optic":
        return RetentionRecommendation(
            action_type="service_review",
            suggested_offer="Fiber service loyalty discount",
            priority="medium",
            reason=("High-risk customer currently uses fiber optic service."),
        )

    return RetentionRecommendation(
        action_type="priority_outreach",
        suggested_offer="Personalized retention offer",
        priority="medium",
        reason="Customer exceeds the retention intervention threshold.",
    )
