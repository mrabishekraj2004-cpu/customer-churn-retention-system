from fastapi import FastAPI

from api.routes.analytics import router as analytics_router
from api.routes.customer import router as customer_router
from api.routes.health import router as health_router
from api.routes.prediction import router as prediction_router
from api.routes.prediction_history import router as prediction_history_router
from api.routes.retention_action import router as retention_action_router
from src.config import settings

app = FastAPI(
    title=settings.app_name,
    description=(
        "API for predicting customer churn risk and supporting retention decisions."
    ),
    version=settings.app_version,
)

app.include_router(health_router)
app.include_router(prediction_router)
app.include_router(prediction_history_router)
app.include_router(retention_action_router)
app.include_router(customer_router)
app.include_router(analytics_router)
