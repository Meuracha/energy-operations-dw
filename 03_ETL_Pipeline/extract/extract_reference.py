"""
Extract reference data for fact_reference_annual: crude oil reference price (EIA),
national energy production/consumption (EPPO), company-level petroleum sales (DMF).

Confidence level per source (verified via web research, not yet tested against
live data since this sandbox cannot reach these hosts):
  - EIA:   HIGH confidence — official REST API, well documented, free API key.
           Confirmed: no Dubai crude series exists in EIA (that's a paid Platts
           product) — using Brent (RBRTE) instead as the closer free proxy.
  - EPPO:  MEDIUM confidence — has an open data catalog (CKAN) + a "Request API"
           page, but you need to register and find the exact dataset/resource ID
           for what you need (national oil production/consumption series)
  - DMF:   MEDIUM confidence — data is published via data.go.th (Thailand's open
           government data portal) as downloadable datasets, not a queryable API.
           Likely means downloading CSV/XLSX directly rather than programmatic pulls.

Run locally:
    pip install requests pandas python-dotenv
    Get an EIA API key: https://www.eia.gov/opendata/register.php
    python extract_reference.py
"""
import requests
import pandas as pd
from pathlib import Path
import os

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

EIA_API_KEY = os.environ.get("EIA_API_KEY", "YOUR_KEY_HERE")


def extract_eia_crude_price():
    """
    Confirmed via EIA documentation: EIA does not carry a Dubai crude series
    (that's a Platts product, paid data). Brent (RBRTE) is the closer, more
    globally-referenced proxy for Asia-Pacific pricing than WTI — still not a
    perfect match for Thailand's actual import mix, but defensible and free.
    State this limitation explicitly in Deliverable #4/#6 documentation.
    """
    url = "https://api.eia.gov/v2/petroleum/pri/spt/data/"
    params = {
        "api_key": EIA_API_KEY,
        "frequency": "weekly",
        "data[0]": "value",
        "facets[series][]": "RBRTE",  # Europe Brent spot price — confirmed to exist in EIA's API
        "sort[0][column]": "period",
        "sort[0][direction]": "asc",
    }
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    records = resp.json()["response"]["data"]
    df = pd.DataFrame(records)
    out_path = OUTPUT_DIR / "fact_reference_crude_price.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows -> {out_path}")
    return df


def extract_eppo_national_energy():
    """
    Confirmed dataset: "ความต้องการใช้และการจัดหาน้ำมันดิบและน้ำมันสำเร็จรูป"
    (national crude oil + refined product demand/supply, monthly, sourced from
    the Department of Energy Business, processed by EPPO) — direct CSV download,
    verified to exist via catalog.eppo.go.th.
    """
    DATASET_CSV_URL = (
        "https://catalog.eppo.go.th/dataset/56945351-658d-4593-9512-8ce15a1350b9/"
        "resource/582a28c6-80ec-45f9-9f12-0050718626a3/download/dataset_11_18.csv"
    )
    resp = requests.get(DATASET_CSV_URL)
    resp.raise_for_status()
    out_path = OUTPUT_DIR / "fact_reference_national_energy_raw.csv"
    out_path.write_bytes(resp.content)
    print(f"Wrote raw file -> {out_path}")
    print("NOTE: inspect this file's actual columns/encoding before using — Thai "
          "government CSVs sometimes need encoding='tis-620' or 'cp874' instead of utf-8, "
          "and column names will need mapping to the segment_id/year grain in the schema.")
    return out_path


def extract_dmf_company_production():
    """
    data.go.th is confirmed CKAN-powered (meta-generator: ckan 2.10.1), same as EPPO's
    catalog — so the standard CKAN package_show API should work here, though this
    specific call hasn't been tested live (blocked in the sandbox that wrote this code).
    Dataset confirmed to exist: "รายงานการขายปิโตรเลียมประจำเดือน" (monthly-petroleum),
    published by DMF, company-level petroleum sales via concessionaire e-receipt system.
    """
    package_show_url = "https://data.go.th/api/3/action/package_show"
    resp = requests.get(package_show_url, params={"id": "monthly-petroleum"})
    resp.raise_for_status()
    package = resp.json()["result"]

    resources = package.get("resources", [])
    if not resources:
        print("No resources found in package — check the dataset still exists at "
              "https://data.go.th/dataset/monthly-petroleum")
        return None

    print(f"Found {len(resources)} resource(s):")
    for r in resources:
        print(f"  - {r.get('name')}: {r.get('url')} ({r.get('format')})")

    # Download the most recent resource (first in list is usually latest, but verify)
    latest = resources[0]
    file_resp = requests.get(latest["url"])
    file_resp.raise_for_status()
    ext = latest.get("format", "xlsx").lower()
    out_path = OUTPUT_DIR / f"fact_dmf_company_production_raw.{ext}"
    out_path.write_bytes(file_resp.content)
    print(f"Wrote raw file -> {out_path}")
    print("NOTE: file is XLS/XLSX per the dataset metadata, not CSV — load with "
          "pd.read_excel() and inspect the actual column structure before mapping "
          "to fact_operations_annual.production_volume_dmf")
    return out_path


if __name__ == "__main__":
    extract_eia_crude_price()
    extract_eppo_national_energy()
    extract_dmf_company_production()
