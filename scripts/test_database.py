from src.database.repositories import CustomerRepository
from src.database.session import SessionLocal

TEST_CUSTOMER_ID = "TEST-0001"


def main() -> None:
    db = SessionLocal()

    try:
        repository = CustomerRepository(db)

        customer = repository.get_by_customer_id(TEST_CUSTOMER_ID)

        if customer is None:
            customer = repository.create(
                customer_id=TEST_CUSTOMER_ID,
                customer_data={
                    "gender": "Male",
                    "senior_citizen": 0,
                    "partner": "No",
                    "dependents": "No",
                    "tenure": 5,
                    "phone_service": "Yes",
                    "multiple_lines": "No",
                    "internet_service": "Fiber optic",
                    "online_security": "No",
                    "online_backup": "No",
                    "device_protection": "No",
                    "tech_support": "No",
                    "streaming_tv": "Yes",
                    "streaming_movies": "Yes",
                    "contract": "Month-to-month",
                    "paperless_billing": "Yes",
                    "payment_method": "Electronic check",
                    "monthly_charges": 89.50,
                    "total_charges": 447.50,
                },
            )

            print("Test customer created.")
        else:
            print("Test customer already exists.")

        print(f"Database ID: {customer.id}")
        print(f"Customer ID: {customer.customer_id}")
        print(f"Contract: {customer.contract}")
        print(f"Monthly charges: {customer.monthly_charges:.2f}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
