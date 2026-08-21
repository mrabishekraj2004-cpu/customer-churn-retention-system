from fastapi import FastAPI

from api.routes.health import router as health_router
from api.routes.prediction import router as prediction_router

app = FastAPI(
    title="Customer Churn Prediction API",
    description=("Predict customer churn risk and support retention decisions."),
    version="1.0.0",
)

app.include_router(health_router)
app.include_router(prediction_router)
