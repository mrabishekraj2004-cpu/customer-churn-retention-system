from api.schemas.customer import (
    CustomerDetailResponse,
    CustomerListResponse,
    CustomerSummaryResponse,
    LatestPredictionResponse,
)
from src.database.models import Customer, Prediction
from src.database.repositories import (
    CustomerRepository,
    PredictionRepository,
)


class CustomerNotFoundError(Exception):
    """Raised when a requested customer does not exist."""


class CustomerService:
    """Provide customer data together with latest churn predictions."""

    def __init__(
        self,
        customer_repository: CustomerRepository,
        prediction_repository: PredictionRepository,
    ) -> None:
        self.customer_repository = customer_repository
        self.prediction_repository = prediction_repository

    def get_customers(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> CustomerListResponse:
        customers = self.customer_repository.get_all(
            limit=limit,
            offset=offset,
        )

        customer_summaries = [
            self._build_customer_summary(customer)
            for customer in customers
        ]

        return CustomerListResponse(
            customers=customer_summaries,
            count=len(customer_summaries),
            limit=limit,
            offset=offset,
        )

    def get_customer(
        self,
        customer_id: str,
    ) -> CustomerDetailResponse:
        customer = self.customer_repository.get_by_customer_id(
            customer_id
        )

        if customer is None:
            raise CustomerNotFoundError(
                f"Customer not found: {customer_id}"
            )

        latest_prediction = self._get_latest_prediction(customer.id)

        return CustomerDetailResponse(
            id=customer.id,
            customer_id=customer.customer_id,
            gender=customer.gender,
            senior_citizen=customer.senior_citizen,
            partner=customer.partner,
            dependents=customer.dependents,
            tenure=customer.tenure,
            phone_service=customer.phone_service,
            multiple_lines=customer.multiple_lines,
            internet_service=customer.internet_service,
            online_security=customer.online_security,
            online_backup=customer.online_backup,
            device_protection=customer.device_protection,
            tech_support=customer.tech_support,
            streaming_tv=customer.streaming_tv,
            streaming_movies=customer.streaming_movies,
            contract=customer.contract,
            paperless_billing=customer.paperless_billing,
            payment_method=customer.payment_method,
            monthly_charges=customer.monthly_charges,
            total_charges=customer.total_charges,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
            latest_prediction=self._build_prediction_response(
                latest_prediction
            ),
        )

    def _build_customer_summary(
        self,
        customer: Customer,
    ) -> CustomerSummaryResponse:
        latest_prediction = self._get_latest_prediction(customer.id)

        return CustomerSummaryResponse(
            id=customer.id,
            customer_id=customer.customer_id,
            tenure=customer.tenure,
            contract=customer.contract,
            internet_service=customer.internet_service,
            monthly_charges=customer.monthly_charges,
            total_charges=customer.total_charges,
            latest_prediction=self._build_prediction_response(
                latest_prediction
            ),
        )

    def _get_latest_prediction(
        self,
        customer_db_id: int,
    ) -> Prediction | None:
        predictions = self.prediction_repository.get_customer_history(
            customer_db_id
        )

        if not predictions:
            return None

        return predictions[0]

    @staticmethod
    def _build_prediction_response(
        prediction: Prediction | None,
    ) -> LatestPredictionResponse | None:
        if prediction is None:
            return None

        return LatestPredictionResponse(
            prediction_id=prediction.id,
            churn_probability=prediction.churn_probability,
            risk_level=prediction.risk_level,
            retention_action_required=(
                prediction.retention_action_required
            ),
            model_version=prediction.model_version,
            created_at=prediction.created_at,
        )