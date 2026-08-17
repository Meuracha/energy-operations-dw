"""
Extract investor/market data (daily prices + annual fundamentals) via yfinance.
This is the easiest source in the pipeline — fully automated, no manual PDF work.

Run locally (this needs internet access to finance.yahoo.com, which the
Claude sandbox does not have):
    pip install yfinance pandas
    python extract_investor.py
"""
import yfinance as yf
import pandas as pd
from pathlib import Path

# dim_company scope, per the locked project scope
TICKERS = {
    "PTTEP.BK": "PTTEP",
    "PTT.BK": "PTT",
    "TOP.BK": "TOP",
    "BCP.BK": "BCP",
    "OR.BK": "OR",
}

START_DATE = "2019-01-01"  # adjust to however many years of history you want
END_DATE = None  # None = up to today

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def extract_daily_prices():
    """fact_investor_daily grain: company x date"""
    all_rows = []
    for ticker, company_id in TICKERS.items():
        hist = yf.download(ticker, start=START_DATE, end=END_DATE, progress=False)
        if hist.empty:
            print(f"WARNING: no data returned for {ticker} — check ticker is still valid")
            continue

        # yfinance returns MultiIndex columns like ('Close', 'PTTEP.BK') even for
        # a single ticker in current versions — flatten to plain 'Close' before
        # selecting, otherwise column selection returns duplicated/mismatched columns
        if isinstance(hist.columns, pd.MultiIndex):
            hist.columns = hist.columns.get_level_values(0)

        hist = hist.reset_index()
        hist["company_id"] = company_id
        hist["ticker"] = ticker
        all_rows.append(hist[["Date", "company_id", "ticker", "Close", "Volume"]])

    if not all_rows:
        print("ERROR: no tickers returned data — check network access and ticker validity "
              "(e.g. OR.BK may need verifying, it listed relatively recently)")
        return pd.DataFrame()

    df = pd.concat(all_rows, ignore_index=True)
    df.columns = ["date_id", "company_id", "ticker", "close_price", "volume"]
    out_path = OUTPUT_DIR / "fact_investor_daily.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows -> {out_path}")
    return df


def extract_annual_fundamentals():
    """
    Supplementary fields for fact_investor_annual that yfinance can provide directly
    (dividend, shares outstanding). Cross-check these against the 56-1 report numbers —
    yfinance figures can lag or be sourced from a data vendor with its own conventions.
    """
    rows = []
    for ticker, company_id in TICKERS.items():
        t = yf.Ticker(ticker)
        info = t.info  # NOTE: yfinance's .info schema changes over time — verify keys locally
        rows.append({
            "company_id": company_id,
            "ticker": ticker,
            "dividend_yield_yf": info.get("dividendYield"),
            "shares_outstanding_yf": info.get("sharesOutstanding"),
            "trailing_pe_yf": info.get("trailingPE"),
        })
    df = pd.DataFrame(rows)
    out_path = OUTPUT_DIR / "fact_investor_annual_yf_supplement.csv"
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows -> {out_path}")
    return df


if __name__ == "__main__":
    extract_daily_prices()
    extract_annual_fundamentals()
