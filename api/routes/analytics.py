from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.schemas.analytics import (
    AnalyticsSummaryResponse,
    RetentionActionMetricsResponse,
    RetentionOutcomeMetricsResponse,
    RiskDistributionResponse,
)
from src.database.repositories import AnalyticsRepository
from src.database.session import get_db
from src.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["analytics"],
)


def get_analytics_service(
    db: Annotated[Session, Depends(get_db)],
) -> AnalyticsService:
    repository = AnalyticsRepository(db)

    return AnalyticsService(repository)


@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
)
def get_analytics_summary(
    service: Annotated[
        AnalyticsService,
        Depends(get_analytics_service),
    ],
) -> AnalyticsSummaryResponse:
    summary = service.get_summary()

    return AnalyticsSummaryResponse(
        total_customers=summary.total_customers,
        total_monthly_revenue=summary.total_monthly_revenue,
        monthly_revenue_at_risk=(summary.monthly_revenue_at_risk),
        annual_revenue_at_risk=(summary.annual_revenue_at_risk),
        expected_monthly_revenue_loss=(summary.expected_monthly_revenue_loss),
        expected_annual_revenue_loss=(summary.expected_annual_revenue_loss),
        customers_with_predictions=(summary.customers_with_predictions),
        high_risk_customers=summary.high_risk_customers,
        average_churn_probability=(summary.average_churn_probability),
        risk_distribution=RiskDistributionResponse(
            low=summary.low_risk_customers,
            medium=summary.medium_risk_customers,
            high=summary.high_risk_level_customers,
            critical=summary.critical_risk_customers,
        ),
        retention_actions=RetentionActionMetricsResponse(
            total=summary.total_retention_actions,
            recommended=summary.recommended_actions,
            in_progress=summary.in_progress_actions,
            completed=summary.completed_actions,
        ),
        retention_outcomes=RetentionOutcomeMetricsResponse(
            retained=summary.retained_customers,
            churned=summary.churned_customers,
            unknown=summary.unknown_outcomes,
            success_rate=summary.retention_success_rate,
        ),
        total_estimated_cost=summary.total_estimated_cost,
        revenue_saved=summary.revenue_saved,
        net_retention_benefit=(summary.net_retention_benefit),
        retention_roi=summary.retention_roi,
    )
