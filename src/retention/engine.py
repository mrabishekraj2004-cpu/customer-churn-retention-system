from typing import Any

from src.retention.rules import (
    get_retention_recommendation,
    get_risk_factors,
)


class RetentionEngine:
    """Generate explainable retention recommendations for customers."""

    def recommend(
        self,
        customer: dict[str, Any],
        churn_probability: float,
        operating_threshold: float,
    ) -> dict[str, Any]:
        risk_factors = get_risk_factors(customer)

        recommendation = get_retention_recommendation(
            customer=customer,
            churn_probability=churn_probability,
            operating_threshold=operating_threshold,
        )

        action_required = churn_probability >= operating_threshold

        return {
            "retention_action_required": action_required,
            "risk_factors": risk_factors,
            "action_type": recommendation.action_type,
            "suggested_offer": recommendation.suggested_offer,
            "priority": recommendation.priority,
            "reason": recommendation.reason,
        }
