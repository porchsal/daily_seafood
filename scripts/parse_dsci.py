"""
parse_dsci.py
-------------
Parses a Customer Item Profitability report (UTF-16, fixed-width columns)
and writes a normalized CSV ready to COPY into staging.customer_item_profitability.

Usage:
    python3 parse_dsci.py                          # uses defaults below
    python3 parse_dsci.py input.txt output.csv     # explicit paths
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# ---------------------------------------------------------------------------
# Column slices — derived from the report header line positions
# ---------------------------------------------------------------------------
COL_CUST_CODE        = slice(0,   11)
COL_CUSTOMER_NAME    = slice(11,  53)
COL_ITEM_CODE        = slice(53,  70)
COL_ITEM_DESCRIPTION = slice(70,  102)
COL_INVOICE_DATE     = slice(102, 116)
COL_INVOICE_NO       = slice(116, 125)
COL_QUANTITY         = slice(125, 140)
COL_PRICE            = slice(140, 155)
COL_AMOUNT           = slice(155, 170)
COL_COST             = slice(170, 185)
COL_PROFIT           = slice(185, 200)
COL_MARGIN           = slice(200, None)

SKIP_PREFIXES = (
    "Customer Item Profitability",
    "From ",
    "Alphabetical Order",
    "Inactive Skipped",
    "All Customers",
    "By Item",
    "Full Line Item Detail",
    "Canadian Dollars",
    "Marketing Costs Not Included",
    "Cust Code",
    "Rpt Total:",
)

CSV_FIELDS = [
    "cust_code", "customer_name", "item_code", "item_description",
    "invoice_date", "invoice_no", "quantity", "price", "amount",
    "cost", "profit", "margin", "source_file",
]


def should_skip(line: str) -> bool:
    s = line.strip()
    return not s or any(s.startswith(p) for p in SKIP_PREFIXES)


def parse_date(value: str) -> str:
    """'Mar  9, 2026' or 'Mar 14, 2026' → '2026-03-09'"""
    return datetime.strptime(" ".join(value.split()), "%b %d, %Y").date().isoformat()


def parse_num(value: str) -> str:
    v = value.strip()
    return str(Decimal(v)) if v else ""


def parse_line(line: str, source_file: str) -> dict:
    return {
        "cust_code":        line[COL_CUST_CODE].strip(),
        "customer_name":    line[COL_CUSTOMER_NAME].strip(),
        "item_code":        line[COL_ITEM_CODE].strip(),
        "item_description": line[COL_ITEM_DESCRIPTION].strip(),
        "invoice_date":     parse_date(line[COL_INVOICE_DATE].strip()),
        "invoice_no":       line[COL_INVOICE_NO].strip(),
        "quantity":         parse_num(line[COL_QUANTITY]),
        "price":            parse_num(line[COL_PRICE]),
        "amount":           parse_num(line[COL_AMOUNT]),
        "cost":             parse_num(line[COL_COST]),
        "profit":           parse_num(line[COL_PROFIT]),
        "margin":           parse_num(line[COL_MARGIN]),
        "source_file":      source_file,
    }


def parse_dsci(input_path: Path, output_path: Path) -> None:
    rows = []
    errors = []

    with input_path.open("r", encoding="utf-16") as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.rstrip("\r\n")
            if should_skip(line):
                continue
            try:
                rows.append(parse_line(line, input_path.name))
            except Exception as exc:
                errors.append((lineno, str(exc), line[:120]))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Rows written : {len(rows)}")
    print(f"✗ Parse errors : {len(errors)}")
    if errors:
        for lineno, msg, preview in errors:
            print(f"  Line {lineno}: {msg} | {preview}")


if __name__ == "__main__":
    input_path  = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/incoming/DSCI.txt")
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/outgoing/DSCI_normalized.csv")
    parse_dsci(input_path, output_path)