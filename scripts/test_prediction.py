from src.models.predict import PredictionService


def main() -> None:
    customer = {
        "SeniorCitizen": 0,
        "tenure": 5,
        "MonthlyCharges": 89.50,
        "TotalCharges": 447.50,
        "gender": "Male",
        "Partner": "No",
        "Dependents": "No",
        "PhoneService": "Yes",
        "MultipleLines": "No",
        "InternetService": "Fiber optic",
        "OnlineSecurity": "No",
        "OnlineBackup": "No",
        "DeviceProtection": "No",
        "TechSupport": "No",
        "StreamingTV": "Yes",
        "StreamingMovies": "Yes",
        "Contract": "Month-to-month",
        "PaperlessBilling": "Yes",
        "PaymentMethod": "Electronic check",
    }

    service = PredictionService()
    prediction = service.predict(customer)

    print("\nCustomer churn prediction")

    for key, value in prediction.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
