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

### 5. Prepare the Dataset and Model

The raw dataset and trained `.joblib` model are intentionally not stored in Git.

Place the Telco Customer Churn dataset at:

```text
data/raw/telco_customer_churn.csv
```

You can inspect the raw dataset with:

```bash
python -m src.data.inspect_data
```

Clean and validate the dataset:

```bash
python -m src.data.clean_data
```

The cleaned dataset will be created at:

```text
data/processed/telco_customer_churn.csv
```

Train the production churn model:

```bash
python -m src.models.train_production
```

The training pipeline generates:

```text
models/churn_pipeline.joblib
models/churn_pipeline_metadata.json
```

The `.joblib` model artifact is ignored by Git and should be generated locally.

See `data/README.md` for additional dataset setup information.

### 6. Initialize the Database

```bash
python scripts/init_db.py
```

This creates the local SQLite database and the application tables:

```text
customers
predictions
retention_actions
```

### 7. Start the API

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

OpenAPI specification:

```text
http://127.0.0.1:8000/openapi.json
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

Example response:

```json
{
  "status": "ok",
  "service": "customer-churn-api"
}
```

### Analytics Summary

```text
GET /api/v1/analytics/summary
```

The analytics endpoint provides churn, revenue-risk, retention, and ROI metrics for business decision support.

## Machine Learning Workflow

The machine learning workflow is:

```text
Raw Telco Customer Dataset
        ↓
Dataset Inspection
        ↓
Data Validation and Cleaning
        ↓
Feature Preprocessing
        ↓
Model Training
        ↓
Model Evaluation
        ↓
Business Evaluation
        ↓
Production Model Training
        ↓
Prediction Service
```

The production model uses a scikit-learn pipeline and Logistic Regression classifier.

The saved production model is loaded by the prediction layer to calculate customer churn probabilities.

## Churn Risk Classification

Customers are classified into risk levels based on predicted churn probability:

```text
Low       < 0.40
Medium    >= 0.40
High      >= 0.60
Critical  >= 0.80
```

The production operating threshold is:

```text
0.80
```

Customers whose churn probability reaches the operating threshold require retention action.

## Business Workflow

The application connects machine-learning predictions with retention operations:

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

## Analytics Logic

### Monthly Revenue at Risk

Monthly revenue associated with customers whose latest prediction requires retention action.

### Annual Revenue at Risk

```text
monthly_revenue_at_risk × 12
```

### Expected Monthly Revenue Loss

Expected monthly revenue loss uses customer monthly revenue and churn probability from the latest applicable prediction.

Conceptually:

```text
Σ(monthly_charges × churn_probability)
```

### Expected Annual Revenue Loss

```text
expected_monthly_revenue_loss × 12
```

### Revenue Saved

Revenue saved represents annualized monthly revenue associated with customers successfully retained through completed retention actions.

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

## Retention Action Lifecycle

Retention recommendations follow this workflow:

```text
recommended
     ↓
in_progress
     ↓
completed
```

A completed retention action requires an outcome.

Examples of outcomes include:

```text
retained
churned
unknown
```

Retention outcomes are used by the analytics layer to measure retention effectiveness.

## Running Tests

Run the complete test suite:

```bash
pytest -q
```

Run individual test areas:

```bash
pytest tests/api -v
pytest tests/database -v
pytest tests/services -v
pytest tests/retention -v
```

The project includes tests for:

- API endpoints
- Database repositories
- Customer services
- Prediction workflows
- Retention recommendation logic
- Retention action lifecycle
- Analytics calculations
- Revenue-risk calculations
- Retention ROI calculations

## Code Quality

Run Ruff:

```bash
ruff check .
```

Format the project:

```bash
ruff format .
```

Then verify:

```bash
ruff check .
```

## Local Files Excluded from Git

The following development artifacts are intentionally excluded from the repository:

```text
.env
.venv/
customer_churn.db
data/raw/telco_customer_churn.csv
data/processed/telco_customer_churn.csv
models/churn_pipeline.joblib
__pycache__/
.pytest_cache/
.ruff_cache/
```

This keeps environment-specific files, local datasets, databases, caches, and generated binary model artifacts out of source control.

## Production Model Metadata

The repository includes production model metadata describing:

- Model name
- Model version
- Training timestamp
- Number of training rows
- Target variable
- Positive class
- Operating threshold
- Numeric features
- Categorical features

The generated binary model itself is recreated locally using:

```bash
python -m src.models.train_production
```

## Project Goal

The goal of this project is not only to predict customer churn but to turn machine-learning predictions into actionable business decisions.

Instead of stopping at model probability output, the system connects predictions with:

- customer risk prioritization,
- retention recommendations,
- retention workflow tracking,
- outcome measurement,
- revenue-risk analysis,
- revenue-saved calculations,
- and retention ROI.

This demonstrates an end-to-end approach to applying machine learning within a business-oriented backend application.