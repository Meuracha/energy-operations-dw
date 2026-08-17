"""
Load raw extracted CSVs into BigQuery tables matching the star schema
from Deliverable #2.

Run locally:
    pip install google-cloud-bigquery pandas
    gcloud auth application-default login   # or set GOOGLE_APPLICATION_CREDENTIALS
    python load_bigquery.py
"""
from google.cloud import bigquery
import pandas as pd
from pathlib import Path

PROJECT_ID = "pttep-energy-dw"          # GCP project ID
DATASET_ID = "energy_dw"                # BigQuery dataset (create in BigQuery first)

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"
QUALITY_DIR = Path(__file__).parent.parent / "data" / "quality"

# maps local CSV -> (source directory, destination table name)
TABLE_MAP = {
    "fact_investor_daily.csv": (RAW_DIR, "fact_investor_daily"),
    "fact_investor_annual_yf_supplement.csv": (RAW_DIR, "fact_investor_annual_yf_supplement"),
    "fact_reference_crude_price.csv": (RAW_DIR, "fact_reference_crude_price"),
    "fact_finance_operations_annual.csv": (PROCESSED_DIR, "fact_finance_operations_annual"),  # output of transform.py — the main fact table
    "data_quality_restatement_checks.csv": (QUALITY_DIR, "data_quality_restatement_checks"),  # Dashboard page 3, card 1
    "data_quality_anomalies.csv": (QUALITY_DIR, "data_quality_anomalies"),                    # Dashboard page 3, card 2
    "currency_conversion_rates.csv": (QUALITY_DIR, "currency_conversion_rates"),               # Dashboard page 3, card 3
}


def load_table(client: bigquery.Client, csv_path: Path, table_name: str):
    df = pd.read_csv(csv_path)
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{table_name}"
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # full refresh; switch to WRITE_APPEND for incremental loads
        autodetect=True,
    )
    job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
    job.result()
    print(f"Loaded {len(df)} rows -> {table_ref}")


def main():
    client = bigquery.Client(project=PROJECT_ID)
    for csv_name, (source_dir, table_name) in TABLE_MAP.items():
        csv_path = source_dir / csv_name
        if not csv_path.exists():
            print(f"SKIP: {csv_path} not found — run the corresponding extract/transform script first")
            continue
        load_table(client, csv_path, table_name)


if __name__ == "__main__":
    main()