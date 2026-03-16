CREATE TABLE warehouse.fact_sales_profitability (
    sales_id BIGSERIAL PRIMARY KEY,
    date_key INTEGER NOT NULL REFERENCES warehouse.dim_date(date_key),
    customer_id BIGINT NOT NULL REFERENCES warehouse.dim_customer(customer_id),
    item_id BIGINT NOT NULL REFERENCES warehouse.dim_item(item_id),
    invoice_no TEXT NOT NULL,
    quantity NUMERIC(18,4),
    unit_price NUMERIC(18,4),
    sales_amount NUMERIC(18,4),
    cost_amount NUMERIC(18,4),
    profit_amount NUMERIC(18,4),    
    margin_pct NUMERIC(18,4),
    source_file TEXT,
    load_timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);