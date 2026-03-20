INSERT INTO warehouse.dim_customer (cust_code, customer_name)
SELECT DISTINCT
    s.cust_code,
    s.customer_name
FROM staging.customer_item_profitability s
WHERE s.cust_code IS NOT NULL
  AND s.customer_name IS NOT NULL
ON CONFLICT (cust_code) DO UPDATE
SET customer_name = EXCLUDED.customer_name;

INSERT INTO warehouse.dim_item (item_code, item_description)
SELECT DISTINCT
    s.item_code,
    s.item_description
FROM staging.customer_item_profitability s
WHERE s.item_code IS NOT NULL
  AND s.item_description IS NOT NULL
ON CONFLICT (item_code) DO UPDATE
SET item_description = EXCLUDED.item_description;

INSERT INTO warehouse.dim_date (
    date_key,
    full_date,
    year,
    month,
    day,
    month_name,
    quarter
)
SELECT DISTINCT
    CAST(TO_CHAR(s.invoice_date, 'YYYYMMDD') AS INTEGER) AS date_key,
    s.invoice_date AS full_date,
    EXTRACT(YEAR FROM s.invoice_date)::INT AS year,
    EXTRACT(MONTH FROM s.invoice_date)::INT AS month,
    EXTRACT(DAY FROM s.invoice_date)::INT AS day,
    TO_CHAR(s.invoice_date, 'Mon') AS month_name,
    EXTRACT(QUARTER FROM s.invoice_date)::INT AS quarter
FROM staging.customer_item_profitability s
WHERE s.invoice_date IS NOT NULL
ON CONFLICT (date_key) DO NOTHING;

INSERT INTO warehouse.fact_sales_profitability (
    date_key,
    customer_id,
    item_id,
    invoice_no,
    quantity,
    unit_price,
    sales_amount,
    cost_amount,
    profit_amount,
    margin_pct,
    source_file
)
SELECT
    CAST(TO_CHAR(s.invoice_date, 'YYYYMMDD') AS INTEGER) AS date_key,
    dc.customer_id,
    di.item_id,
    s.invoice_no,
    s.quantity,
    s.price,
    s.amount,
    s.cost,
    s.profit,
    s.margin,
    s.source_file
FROM staging.customer_item_profitability s
INNER JOIN warehouse.dim_customer dc
    ON dc.cust_code = s.cust_code
INNER JOIN warehouse.dim_item di
    ON di.item_code = s.item_code
WHERE s.invoice_date IS NOT NULL
ON CONFLICT DO NOTHING;