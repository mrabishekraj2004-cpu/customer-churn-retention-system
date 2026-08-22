from fastapi import FastAPI

from api.routes.prediction import router as prediction_router
from api.routes.prediction_history import router as prediction_history_router
from api.routes.retention_action import router as retention_action_router

app = FastAPI(
    title="Customer Churn Prediction API",
    description=(
        "API for predicting customer churn risk and supporting "
        "retention decisions."
    ),
    version="1.0.0",
)

app.include_router(prediction_router)
app.include_router(prediction_history_router)
app.include_router(retention_action_router)


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "customer-churn-api",
    }