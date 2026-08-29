import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.exception_handlers import register_exception_handlers
from api.middleware.request_logging import log_requests
from api.routes.analytics import router as analytics_router
from api.routes.auth import router as auth_router
from api.routes.customer import router as customer_router
from api.routes.health import router as health_router
from api.routes.prediction import router as prediction_router
from api.routes.prediction_history import router as prediction_history_router
from api.routes.retention_action import router as retention_action_router
from api.routes.user import router as user_router
from src.config import settings
from src.database.initialization import initialize_database
from src.logging_config import configure_logging
from src.security.tokens import validate_jwt_configuration

configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize dependencies and log application lifecycle events."""

    logger.info(
        "Starting %s version %s in %s environment",
        settings.app_name,
        settings.app_version,
        settings.environment,
    )

    validate_jwt_configuration()
    initialize_database()

    yield

    logger.info(
        "Shutting down %s",
        settings.app_name,
    )


app = FastAPI(
    title=settings.app_name,
    description=(
        "API for predicting customer churn risk and supporting retention decisions."
    ),
    version=settings.app_version,
    lifespan=lifespan,
)

app.middleware("http")(log_requests)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(prediction_router)
app.include_router(prediction_history_router)
app.include_router(retention_action_router)
app.include_router(customer_router)
app.include_router(analytics_router)
