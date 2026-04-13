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
import shutil
from datetime import datetime
from decimal import Decimal
from pathlib import Path

# ---------------------------------------------------------------------------
# Column slices
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
    "invoice_date", "invoice_no", "quantity", "price",
    "amount", "cost", "profit", "margin", "source_file",
]


def should_skip(line: str) -> bool:
    s = line.strip()
    return not s or any(s.startswith(p) for p in SKIP_PREFIXES)


def parse_date(value: str) -> str:
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


def process_file(input_path: Path, output_path: Path) -> None:
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


def main():
    incoming_dir = Path("data/incoming")
    processed_dir = Path("data/processed")
    output_dir = Path("data/outgoing")

    processed_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = list(incoming_dir.glob("*.txt"))

    if not files:
        print("No files found in incoming folder.")
        return

    for file in files:
        print(f"\nProcessing: {file.name}")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_file = output_dir / f"{file.stem}_normalized_{timestamp}.csv"
        try:
            process_file(file, output_file)

            # mover archivo a processed
            destination = processed_dir / file.name
            shutil.move(str(file), str(destination))

            print(f"Moved to processed: {destination}")

        except Exception as e:
            print(f"Error processing {file.name}: {e}")


if __name__ == "__main__":
    main()