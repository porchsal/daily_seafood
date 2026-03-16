CREATE TABLE staging.customer_item_profitability (
    id BIGSERIAL PRIMARY KEY,
    cust_code TEXT,
    customer_name TEXT,
    item_code TEXT,
    item_description TEXT,
    invoice_date DATE,
    invoice_no TEXT,
    quantity NUMERIC(18,4),
    price NUMERIC(18,4),
    cost NUMERIC(18,4),
    profit NUMERIC(18,4),
    margin NUMERIC(18,4),
    source_file TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()

);