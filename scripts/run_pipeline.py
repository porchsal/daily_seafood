from __future__ import annotations

import csv
import shutil
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import psycopg

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

DB_CONFIG = {
    "host": "localhost",
    "dbname": "daily_seafood_reporting",
    "user": "postgres",
    "password": "postgres",
    "port": 5432,
}

BASE_DIR = Path("/home/porchsal/igs/daily_seafood")
INCOMING_DIR = BASE_DIR / "data" / "incoming"
OUTGOING_DIR = BASE_DIR / "data" / "outgoing"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FAILED_DIR = BASE_DIR / "data" / "failed"

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
    "cust_code",
    "customer_name",
    "item_code",
    "item_description",
    "invoice_date",
    "invoice_no",
    "quantity",
    "price",
    "amount",
    "cost",
    "profit",
    "margin",
    "source_file",
]

# ---------------------------------------------------------------------------
# PARSER
# ---------------------------------------------------------------------------

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

def process_file(input_path: Path, output_path: Path) -> int:
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

    print(f"Parsed rows: {len(rows)}")
    print(f"Parse errors: {len(errors)}")

    if errors:
        for lineno, msg, preview in errors[:20]:
            print(f"Line {lineno}: {msg} | {preview}")

    return len(rows)

# ---------------------------------------------------------------------------
# DATABASE LOAD
# ---------------------------------------------------------------------------

def load_csv_to_staging(csv_path: Path) -> None:
    copy_sql = """
        COPY staging.customer_item_profitability
        (
            cust_code,
            customer_name,
            item_code,
            item_description,
            invoice_date,
            invoice_no,
            quantity,
            price,
            amount,
            cost,
            profit,
            margin,
            source_file
        )
        FROM STDIN WITH CSV HEADER
    """

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            with csv_path.open("r", encoding="utf-8") as f:
                with cur.copy(copy_sql) as copy:
                    while True:
                        chunk = f.read(8192)
                        if not chunk:
                            break
                        copy.write(chunk)

def run_warehouse_load() -> None:
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("CALL warehouse.process_daily_seafood_load();")
        conn.commit()

# ---------------------------------------------------------------------------
# MAIN PIPELINE
# ---------------------------------------------------------------------------

def main() -> None:
    for directory in (INCOMING_DIR, OUTGOING_DIR, PROCESSED_DIR, FAILED_DIR):
        directory.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(INCOMING_DIR.glob("*.txt"))

    if not txt_files:
        print("No files found in incoming.")
        return

    for txt_file in txt_files:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_file = OUTGOING_DIR / f"{txt_file.stem}_{timestamp}_normalized.csv"
        processed_file = PROCESSED_DIR / f"{txt_file.stem}_{timestamp}.txt"
        failed_file = FAILED_DIR / f"{txt_file.stem}_{timestamp}.txt"

        print(f"\nProcessing file: {txt_file.name}")

        try:
            row_count = process_file(txt_file, csv_file)

            if row_count == 0:
                raise ValueError("No rows parsed from source file.")

            print(f"Loading CSV into staging: {csv_file.name}")
            load_csv_to_staging(csv_file)

            print("Running warehouse load procedure...")
            run_warehouse_load()

            shutil.move(str(txt_file), str(processed_file))
            print(f"Moved original file to processed: {processed_file}")

        except Exception as e:
            print(f"ERROR processing {txt_file.name}: {e}")
            if txt_file.exists():
                shutil.move(str(txt_file), str(failed_file))
                print(f"Moved original file to failed: {failed_file}")

if __name__ == "__main__":
    main()