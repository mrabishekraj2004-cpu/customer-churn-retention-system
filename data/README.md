# Dataset Setup

This project uses the Telco Customer Churn dataset for model development and training.

The dataset files are intentionally excluded from Git so that local data files are not committed to the repository.

## Expected Files

Place the raw dataset at:

```text
data/raw/telco_customer_churn.csv
```

The cleaning pipeline generates:

```text
data/processed/telco_customer_churn.csv
```

## Prepare the Dataset

After placing the raw CSV in `data/raw/`, run:

```bash
python -m src.data.clean_data
```

You can inspect the raw dataset with:

```bash
python -m src.data.inspect_data
```

## Train the Production Model

After cleaning the dataset, run:

```bash
python -m src.models.train_production
```

This creates:

```text
models/churn_pipeline.joblib
models/churn_pipeline_metadata.json
```

The `.joblib` model artifact is intentionally ignored by Git and should be generated locally.