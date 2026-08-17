"""
Semi-automated extraction helper for 56-1 One Report PDFs (Finance + Operations data).

Reality check (per the feasibility review): these are long narrative annual reports,
not structured tables. Full automation is not realistic without a lot of
brittle, report-specific parsing. This script instead:
  1. Pulls all text out of a downloaded 56-1 PDF
  2. Searches for lines near known financial/operational keywords (Thai + English)
  3. Prints candidate lines with page numbers so you can manually verify the
     correct figure and enter it into the CSV template below

This keeps a human in the loop for accuracy (which matters — these numbers
get defended in an interview) while still saving time versus reading the
whole report page by page.

Run locally:
    pip install pdfplumber pandas
    python extract_finance_operations.py path/to/pttep_56-1_2025.pdf
"""
import sys
import re
from pathlib import Path
import pandas as pd

KEYWORDS = {
    "revenue": ["รายได้รวม", "total revenue", "รายได้จากการขาย", "sales revenue", "sales and service income",
                "revenue from sale", "total revenues and income"],
    "net_income": ["กำไรสุทธิ", "net income", "profit for the year"],
    "tax_expense": ["ภาษีเงินได้", "income tax expense"],
    "interest_expense": ["ต้นทุนทางการเงิน", "finance cost", "interest expense"],
    "depreciation_amortization": ["ค่าเสื่อมราคา", "depreciation and amortization", "depreciation, depletion",
                                    "depletion, depreciation", "DD&A", "depletion"],
    "capex": ["รายจ่ายลงทุน", "capital expenditure", "capex"],
    "opex": ["ค่าใช้จ่ายดำเนินงาน", "operating expense", "cost of sales", "cost of goods sold",
             "cost of revenue", "administrative expenses"],
    "production_volume": ["ปริมาณการผลิต", "production volume", "sales volume"],
    "reserves": ["ปริมาณสำรอง", "proved reserves", "1P", "2P", "3P"],
}


def find_candidate_lines(pdf_path: str):
    import pdfplumber

    results = {key: [] for key in KEYWORDS}
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            for line in text.split("\n"):
                for field, kws in KEYWORDS.items():
                    if any(kw.lower() in line.lower() for kw in kws):
                        results[field].append((page_num, line.strip()))

    for field, matches in results.items():
        print(f"\n=== {field} ({len(matches)} candidate lines) ===")
        for page_num, line in matches[:10]:  # cap output, most reports repeat the summary figure
            print(f"  p.{page_num}: {line}")
    return results


def extract_table_from_page(pdf_path: str, page_number: int, table_index: int = 0):
    """
    Extract a structured table from a specific page using pdfplumber's built-in
    table detection — works well for grid-based tables with clear cell borders
    (income statement, cash flow statement). Less reliable for tables with heavily
    merged/nested headers (e.g. the reserves table's Domestic/Foreign/Total under
    Crude/Gas/BOE) — for those, reading the page manually is more reliable than
    debugging a fragile parser.

    page_number is 1-indexed (matching what you see in a PDF reader), not 0-indexed.

    Usage:
        python extract_finance_operations.py path/to/report.pdf --table 360
    """
    import pdfplumber

    with pdfplumber.open(pdf_path) as pdf:
        if page_number < 1 or page_number > len(pdf.pages):
            print(f"ERROR: page {page_number} out of range (document has {len(pdf.pages)} pages)")
            return None
        page = pdf.pages[page_number - 1]
        tables = page.extract_tables()

    if not tables:
        print(f"No tables detected on page {page_number} — this page's layout may not "
              "have clear cell borders. Try reading it manually instead.")
        return None

    if table_index >= len(tables):
        print(f"Only {len(tables)} table(s) found on page {page_number}, "
              f"but table_index={table_index} was requested")
        return None

    raw_table = tables[table_index]
    df = pd.DataFrame(raw_table[1:], columns=raw_table[0])
    print(f"Extracted table from page {page_number} ({len(tables)} table(s) found on this page):")
    print(df.to_string())
    print()
    print("VERIFY: check that column headers and row labels above match the PDF page "
          "before trusting these numbers — table detection can silently misalign cells "
          "on complex layouts.")
    return df


TEMPLATE_COLUMNS = [
    "company_id", "year", "revenue", "net_income", "tax_expense",
    "interest_expense", "depreciation_amortization", "capex", "opex",
    "production_volume_boe", "reserves_1p", "reserves_2p", "reserves_3p",
    "report_name", "document_type", "source", "report_url",
]


def create_manual_entry_template(out_path="../data/raw/manual_entry_template.csv"):
    """Run once to create the CSV you'll fill in by hand after reviewing candidate lines."""
    df = pd.DataFrame(columns=TEMPLATE_COLUMNS)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Template created at {out_path} — fill in one row per company x year")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python extract_finance_operations.py path/to/report.pdf              # scan for candidate lines")
        print("  python extract_finance_operations.py path/to/report.pdf --table 360  # extract structured table from page 360")
        create_manual_entry_template()
    elif len(sys.argv) >= 4 and sys.argv[2] == "--table":
        page_num = int(sys.argv[3])
        extract_table_from_page(sys.argv[1], page_num)
    else:
        find_candidate_lines(sys.argv[1])