# Enterprise Data Warehouse for Energy Operations Intelligence

Portfolio project for PTTEP Services Limited — Business & Data Analyst application.

## Project Structure

```
PTTEP_Project_Scope.md              ← Full project overview (read this first; in Thai)
01_Requirement_Gathering.md         ← Deliverable #1: Simulated stakeholder interviews (in Thai)
02_Star_Schema_Design.md            ← Deliverable #2: Star schema + conformed dimensions (in Thai)
03_ETL_Pipeline/                    ← Deliverable #3: ETL code (Docker-ready — see README inside)
04_Data_Quality_Assessment.md       ← Deliverable #4: Data quality framework and real findings (in Thai)
05_Dashboard_Design_Blueprint.md    ← Deliverable #5: Dashboard design spec + build notes (in Thai)
```

## Status

- ✅ Deliverable #1: Requirement-gathering document
- ✅ Deliverable #2: Star schema + conformed dimensions
- ✅ Deliverable #3: ETL pipeline — **complete**, with real verified data across all 5 companies (PTTEP, PTT, TOP, BCP, OR) × 3 years (2023-2025); Docker-ready; loaded into BigQuery (7 tables, live-tested)
- ✅ Deliverable #4: Data quality assessment — real findings recorded (zero restatements found across 30+ cross-report checks; one flagged anomaly in BCP's 2024 tax expense)
- ✅ Deliverable #5: Looker Studio dashboard — **live and connected to BigQuery**, 3 pages built and finalized (Executive Overview, Company Deep-dive, Data Quality)
- ✅ Deliverable #6: Architecture/best-practice documentation

## Dashboard Preview

### Executive Overview

<img src="https://raw.githubusercontent.com/Meuracha/energy-operations-dw/main/03_ETL_Pipeline/screenshots/dashboard-01-overview.png" width="100%">

### Company Deep-dive

<img src="https://raw.githubusercontent.com/Meuracha/energy-operations-dw/main/03_ETL_Pipeline/screenshots/dashboard-02-deepdive.png" width="100%">

### Data Quality

<img src="https://raw.githubusercontent.com/Meuracha/energy-operations-dw/main/03_ETL_Pipeline/screenshots/dashboard-03-dataquality.png" width="100%">

## Value Chain Margin Spectrum (2025, real verified data)

| Company | Position | EBITDA Margin |
|---|---|---|
| PTTEP | Pure upstream (E&P) | 71.9% |
| PTT | Integrated (large) | 14.9% |
| TOP | Pure downstream (refining) | 7.2% |
| BCP | Integrated (small) | 5.7% |
| OR | Pure retail/marketing | 3.4% |

Margin scales cleanly with proximity to upstream — this is the core insight the dashboard is built around, backed by verified figures from each company's own 56-1 One Report / Annual Report filings.

## Running the ETL Pipeline with Docker

```bash
cd 03_ETL_Pipeline
docker build -t pttep-dw-etl .
docker run -it --rm -v $(pwd)/data:/app/data --env-file .env pttep-dw-etl
python transform/transform.py
```

Verified source data already lives in `03_ETL_Pipeline/data/raw/manual_entry_verified.csv` — no additional setup needed to reproduce the transform step.

Full pipeline details: see `03_ETL_Pipeline/README.md`.