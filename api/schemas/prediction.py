from typing import Literal

from pydantic import BaseModel, Field

YesNo = Literal["Yes", "No"]


class CustomerFeatures(BaseModel):
    customer_id: str = Field(
        min_length=1,
        max_length=50,
    )

    SeniorCitizen: Literal[0, 1]
    tenure: int = Field(ge=0, le=100)
    MonthlyCharges: float = Field(ge=0)
    TotalCharges: float = Field(ge=0)

    gender: Literal["Female", "Male"]
    Partner: YesNo
    Dependents: YesNo
    PhoneService: YesNo

    MultipleLines: Literal[
        "Yes",
        "No",
        "No phone service",
    ]

    InternetService: Literal[
        "DSL",
        "Fiber optic",
        "No",
    ]

    OnlineSecurity: Literal[
        "Yes",
        "No",
        "No internet service",
    ]

    OnlineBackup: Literal[
        "Yes",
        "No",
        "No internet service",
    ]

    DeviceProtection: Literal[
        "Yes",
        "No",
        "No internet service",
    ]

    TechSupport: Literal[
        "Yes",
        "No",
        "No internet service",
    ]

    StreamingTV: Literal[
        "Yes",
        "No",
        "No internet service",
    ]

    StreamingMovies: Literal[
        "Yes",
        "No",
        "No internet service",
    ]

    Contract: Literal[
        "Month-to-month",
        "One year",
        "Two year",
    ]

    PaperlessBilling: YesNo

    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ]


class PredictionResponse(BaseModel):
    prediction_id: int
    customer_id: str
    churn_probability: float
    risk_level: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ]
    retention_action_required: bool
    operating_threshold: float
    model_version: str
