from dataclasses import dataclass

from src.database.models import Prediction
from src.database.repositories import AnalyticsRepository


@dataclass(frozen=True)
class AnalyticsSummary:
    total_customers: int
    total_monthly_revenue: float

    monthly_revenue_at_risk: float
    annual_revenue_at_risk: float

    expected_monthly_revenue_loss: float
    expected_annual_revenue_loss: float

    customers_with_predictions: int
    high_risk_customers: int
    average_churn_probability: float

    low_risk_customers: int
    medium_risk_customers: int
    high_risk_level_customers: int
    critical_risk_customers: int

    total_retention_actions: int
    recommended_actions: int
    in_progress_actions: int
    completed_actions: int

    retained_customers: int
    churned_customers: int
    unknown_outcomes: int

    retention_success_rate: float
    total_estimated_cost: float


class AnalyticsService:
    """Calculate business analytics from churn and retention data."""

    def __init__(
        self,
        repository: AnalyticsRepository,
    ) -> None:
        self.repository = repository

    def get_summary(self) -> AnalyticsSummary:
        latest_predictions = self.repository.get_latest_predictions()

        customers_with_predictions = len(latest_predictions)

        high_risk_customers = sum(
            1
            for prediction in latest_predictions
            if prediction.retention_action_required
        )

        average_churn_probability = self._average_churn_probability(latest_predictions)

        risk_counts = self._risk_counts(latest_predictions)

        total_retention_actions = self.repository.get_total_retention_actions()

        recommended_actions = self.repository.get_retention_action_count_by_status(
            "recommended"
        )

        in_progress_actions = self.repository.get_retention_action_count_by_status(
            "in_progress"
        )

        completed_actions = self.repository.get_retention_action_count_by_status(
            "completed"
        )

        retained_customers = self.repository.get_retention_action_count_by_outcome(
            "retained"
        )

        churned_customers = self.repository.get_retention_action_count_by_outcome(
            "churned"
        )

        unknown_outcomes = self.repository.get_retention_action_count_by_outcome(
            "unknown"
        )

        retention_success_rate = self._retention_success_rate(
            retained=retained_customers,
            churned=churned_customers,
        )

        monthly_revenue_at_risk = self.repository.get_monthly_revenue_at_risk()

        expected_monthly_revenue_loss = (
            self.repository.get_expected_monthly_revenue_loss()
        )

        annual_revenue_at_risk = monthly_revenue_at_risk * 12

        expected_annual_revenue_loss = expected_monthly_revenue_loss * 12

        return AnalyticsSummary(
            total_customers=self.repository.get_total_customers(),
            total_monthly_revenue=(self.repository.get_total_monthly_revenue()),
            monthly_revenue_at_risk=monthly_revenue_at_risk,
            annual_revenue_at_risk=annual_revenue_at_risk,
            expected_monthly_revenue_loss=(expected_monthly_revenue_loss),
            expected_annual_revenue_loss=(expected_annual_revenue_loss),
            customers_with_predictions=customers_with_predictions,
            high_risk_customers=high_risk_customers,
            average_churn_probability=(average_churn_probability),
            low_risk_customers=risk_counts["low"],
            medium_risk_customers=risk_counts["medium"],
            high_risk_level_customers=risk_counts["high"],
            critical_risk_customers=risk_counts["critical"],
            total_retention_actions=total_retention_actions,
            recommended_actions=recommended_actions,
            in_progress_actions=in_progress_actions,
            completed_actions=completed_actions,
            retained_customers=retained_customers,
            churned_customers=churned_customers,
            unknown_outcomes=unknown_outcomes,
            retention_success_rate=retention_success_rate,
            total_estimated_cost=(self.repository.get_total_estimated_cost()),
        )

    @staticmethod
    def _average_churn_probability(
        predictions: list[Prediction],
    ) -> float:
        if not predictions:
            return 0.0

        total_probability = sum(
            prediction.churn_probability for prediction in predictions
        )

        return total_probability / len(predictions)

    @staticmethod
    def _risk_counts(
        predictions: list[Prediction],
    ) -> dict[str, int]:
        counts = {
            "low": 0,
            "medium": 0,
            "high": 0,
            "critical": 0,
        }

        for prediction in predictions:
            if prediction.risk_level in counts:
                counts[prediction.risk_level] += 1

        return counts

    @staticmethod
    def _retention_success_rate(
        retained: int,
        churned: int,
    ) -> float:
        resolved_outcomes = retained + churned

        if resolved_outcomes == 0:
            return 0.0

        return retained / resolved_outcomes * 100
