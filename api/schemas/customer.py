from datetime import datetime

from pydantic import BaseModel


class LatestPredictionResponse(BaseModel):
    prediction_id: int
    churn_probability: float
    risk_level: str
    retention_action_required: bool
    model_version: str
    created_at: datetime


class CustomerSummaryResponse(BaseModel):
    id: int
    customer_id: str
    tenure: int
    contract: str
    internet_service: str
    monthly_charges: float
    total_charges: float
    latest_prediction: LatestPredictionResponse | None = None


class CustomerDetailResponse(BaseModel):
    id: int
    customer_id: str

    gender: str
    senior_citizen: int
    partner: str
    dependents: str

    tenure: int

    phone_service: str
    multiple_lines: str

    internet_service: str
    online_security: str
    online_backup: str
    device_protection: str
    tech_support: str
    streaming_tv: str
    streaming_movies: str

    contract: str
    paperless_billing: str
    payment_method: str

    monthly_charges: float
    total_charges: float

    created_at: datetime
    updated_at: datetime

    latest_prediction: LatestPredictionResponse | None = None


class CustomerListResponse(BaseModel):
    customers: list[CustomerSummaryResponse]
    count: int
    limit: int
    offset: int


class HighRiskCustomerResponse(BaseModel):
    id: int
    customer_id: str
    tenure: int
    contract: str
    internet_service: str
    monthly_charges: float
    churn_probability: float
    risk_level: str
    prediction_id: int
    predicted_at: datetime


class HighRiskCustomerListResponse(BaseModel):
    customers: list[HighRiskCustomerResponse]
    count: int
    limit: int
    offset: int