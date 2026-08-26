# Customer Churn Prediction + Retention Action System

An end-to-end machine learning and backend system for predicting customer churn, identifying high-risk customers, recommending retention actions, tracking retention outcomes, and measuring the financial impact of retention efforts.

The project combines data science, machine learning, backend API development, database persistence, automated testing, and business analytics.

## Features

### Customer Churn Prediction

- Predict customer churn probability.
- Assign customer risk levels.
- Identify customers requiring retention action.
- Store prediction results.
- Maintain customer prediction history.

### Customer Management

- Store customer information.
- Retrieve customer records.
- Maintain customer prediction data.
- Support repeated predictions for existing customers.

### Retention Action System

- Generate retention recommendations for high-risk customers.
- Store recommended retention actions.
- Track retention action status.
- Support the workflow:
  - `recommended`
  - `in_progress`
  - `completed`
- Record retention outcomes.
- Track retained and churned customers.

### Analytics

The analytics API provides business and churn metrics including:

- Total customers
- Total monthly revenue
- Customers with predictions
- High-risk customers
- Average churn probability
- Risk distribution
- Retention action counts
- Retention outcomes
- Retention success rate
- Monthly revenue at risk
- Annual revenue at risk
- Expected monthly revenue loss
- Expected annual revenue loss
- Total estimated retention cost
- Revenue saved
- Net retention benefit
- Retention ROI

## Technology Stack

### Machine Learning

- Python
- pandas
- NumPy
- scikit-learn
- joblib

### Backend

- FastAPI
- Pydantic
- SQLAlchemy
- Uvicorn

### Database

- SQLite for local development
- SQLAlchemy ORM

### Testing and Code Quality

- pytest
- Ruff

## Project Structure

```text
customer-churn-retention-system/
├── api/
│   ├── routes/
│   ├── schemas/
│   └── main.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── README.md
├── models/
├── scripts/
├── src/
│   ├── data/
│   ├── database/
│   ├── features/
│   ├── models/
│   ├── retention/
│   └── services/
├── tests/
│   ├── api/
│   ├── database/
│   ├── retention/
│   └── services/
├── .env.example
├── .gitignore
├── README.md
└── requirements.txt
```

## Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd customer-churn-retention-system
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example configuration:

```bash
cp .env.example .env
```

The default database configuration is:

```env
DATABASE_URL=sqlite:///./customer_churn.db
```

### 5. Initialize the database

```bash
python scripts/init_db.py
```

### 6. Start the API

```bash
uvicorn api.main:app --reload
```

The API will be available locally at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation:

```text
http://127.0.0.1:8000/docs
```

## Main API Areas

The application includes APIs for:

- Health checks
- Customer management
- Churn prediction
- Prediction history
- Retention actions
- Retention action queue
- Business analytics

### Health Check

```text
GET /health
```

### Analytics Summary

```text
GET /api/v1/analytics/summary
```

The analytics endpoint provides churn, revenue-risk, retention, and ROI metrics for business decision support.

## Analytics Logic

### Monthly Revenue at Risk

Monthly revenue associated with customers whose latest prediction requires retention action.

### Annual Revenue at Risk

```text
monthly_revenue_at_risk × 12
```

### Expected Monthly Revenue Loss

Expected loss is calculated using customer monthly revenue and churn probability from the latest prediction.

Conceptually:

```text
Σ(monthly_charges × churn_probability)
```

### Expected Annual Revenue Loss

```text
expected_monthly_revenue_loss × 12
```

### Revenue Saved

Annualized monthly revenue associated with customers successfully retained through completed retention actions.

```text
retained_monthly_revenue × 12
```

### Net Retention Benefit

```text
revenue_saved - total_estimated_cost
```

### Retention ROI

When retention cost is greater than zero:

```text
((revenue_saved - retention_cost) / retention_cost) × 100
```

## Running Tests

Run the complete test suite:

```bash
pytest -q
```

Run a specific test area:

```bash
pytest tests/api -v
pytest tests/database -v
pytest tests/services -v
pytest tests/retention -v
```

## Code Quality

Check the project with Ruff:

```bash
ruff check .
```

Format the project:

```bash
ruff format .
```

Then verify formatting and linting:

```bash
ruff check .
```

## Machine Learning Workflow

The project contains separate modules for:

1. Dataset inspection
2. Data cleaning
3. Feature preprocessing
4. Model training
5. Model evaluation
6. Business evaluation
7. Production model training
8. Prediction
9. Retention decision support

The trained production pipeline is loaded by the prediction layer to generate churn probabilities used by the retention system.

## Business Workflow

The overall application workflow is:

```text
Customer Data
     ↓
Churn Prediction
     ↓
Risk Classification
     ↓
Retention Decision
     ↓
Retention Recommendation
     ↓
Retention Action Tracking
     ↓
Outcome Recording
     ↓
Business Analytics
     ↓
Revenue Saved / ROI
```

## Project Goal

The goal of this project is not only to predict churn but to turn machine-learning predictions into actionable business decisions.

Instead of stopping at model probability output, the system connects predictions with:

- customer risk prioritization,
- retention recommendations,
- retention workflow tracking,
- outcome measurement,
- revenue-risk analysis,
- and retention ROI.

This demonstrates an end-to-end approach to using machine learning in a business application.