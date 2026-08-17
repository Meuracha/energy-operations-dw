"""
Transform raw extracted data into the final fact tables, applying the
calculations and assumptions locked in Deliverable #1 (assumptions) and
Deliverable #2 (schema).

Run locally after the extract scripts have produced their CSVs:
    python transform.py
"""
import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
OUT_DIR = Path(__file__).parent.parent / "data" / "processed"
OUT_DIR.mkdir(parents=True, exist_ok=True)

BOE_CONVERSION_FACTOR = 6000  # 1 BOE ≈ 6,000 scf natural gas — assumption per Deliverable #1
DATA_QUALITY_THRESHOLD = 0.05  # flag if company-reported vs DMF production differs >5%


def compute_ebitda(df: pd.DataFrame) -> pd.DataFrame:
    df["ebitda"] = (
        df["net_income"] + df["tax_expense"] + df["interest_expense"] + df["depreciation_amortization"]
    )
    df["ebitda_margin"] = df["ebitda"] / df["revenue"]
    df["capex_revenue_ratio"] = df["capex"] / df["revenue"]
    return df


def flag_production_discrepancy(df: pd.DataFrame) -> pd.DataFrame:
    """
    IMPORTANT: DMF's data is published at the field/concession level (e.g. เอราวัณ,
    บงกช, สิริกิติ์, อาทิตย์) — not by company directly, and per the field-to-company
    mapping in reference_data/field_to_company_mapping.csv, virtually every major
    domestic field is operated by PTTEP. TOP, BCP, and OR are downstream companies
    (refining/retail) that don't produce petroleum domestically at all — they buy
    crude and refine/sell it. So this cross-check is only meaningful for PTTEP;
    other companies should have production_volume_dmf = NULL, not a fabricated value.

    Expects columns production_volume_boe (company-reported, from 56-1) and
    production_volume_dmf (aggregated from DMF field-level data via the mapping,
    PTTEP only). Computes % difference and flags rows that exceed
    DATA_QUALITY_THRESHOLD for rows where a DMF comparison value actually exists.
    """
    df["production_pct_diff"] = pd.NA
    df["data_quality_flag"] = pd.NA

    has_comparison = df["production_volume_dmf"].notna()
    df.loc[has_comparison, "production_pct_diff"] = (
        (df.loc[has_comparison, "production_volume_boe"] - df.loc[has_comparison, "production_volume_dmf"]).abs()
        / df.loc[has_comparison, "production_volume_dmf"]
    )
    df.loc[has_comparison, "data_quality_flag"] = df.loc[has_comparison, "production_pct_diff"] > DATA_QUALITY_THRESHOLD

    non_pttep_with_data = df[(df["company_id"] != "PTTEP") & has_comparison]
    if len(non_pttep_with_data) > 0:
        print(f"WARNING: {len(non_pttep_with_data)} non-PTTEP rows have a DMF comparison "
              "value — verify this is intentional, since TOP/BCP/OR don't produce "
              "petroleum domestically and shouldn't have this field populated")

    return df


def compute_market_share(company_production: pd.DataFrame, national_production: pd.DataFrame) -> pd.DataFrame:
    """
    Joins through dim_date + dim_energy_segment only (never directly joining
    fact_operations to fact_reference on a shared grain) — per the join
    design decided in Deliverable #2.
    """
    merged = company_production.merge(
        national_production, on=["year", "segment_id"], suffixes=("_company", "_national")
    )
    merged["market_share"] = merged["production_volume_boe"] / merged["national_production"]
    return merged


if __name__ == "__main__":
    finance_path = RAW_DIR / "manual_entry_verified.csv"  # single source of truth — filled in by hand after PDF review
    if finance_path.exists():
        df = pd.read_csv(finance_path)
        df = compute_ebitda(df)
        if "production_volume_dmf" in df.columns:
            df = flag_production_discrepancy(df)
        df.to_csv(OUT_DIR / "fact_finance_operations_annual.csv", index=False)
        print(f"Wrote {len(df)} transformed rows -> {OUT_DIR / 'fact_finance_operations_annual.csv'}")
    else:
        print(f"SKIP: {finance_path} not found — fill in the manual entry template first "
              "(see extract_finance_operations.py)")