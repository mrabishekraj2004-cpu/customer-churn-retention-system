from pydantic import BaseModel


class RiskDistributionResponse(BaseModel):
    low: int
    medium: int
    high: int
    critical: int


class RetentionActionMetricsResponse(BaseModel):
    total: int
    recommended: int
    in_progress: int
    completed: int


class RetentionOutcomeMetricsResponse(BaseModel):
    retained: int
    churned: int
    unknown: int
    success_rate: float


class AnalyticsSummaryResponse(BaseModel):
    total_customers: int
    total_monthly_revenue: float

    monthly_revenue_at_risk: float
    annual_revenue_at_risk: float

    expected_monthly_revenue_loss: float
    expected_annual_revenue_loss: float

    customers_with_predictions: int
    high_risk_customers: int
    average_churn_probability: float

    risk_distribution: RiskDistributionResponse

    retention_actions: RetentionActionMetricsResponse
    retention_outcomes: RetentionOutcomeMetricsResponse

    total_estimated_cost: float

    revenue_saved: float
    net_retention_benefit: float
    retention_roi: float
