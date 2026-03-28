CREATE OR REPLACE VIEW mart.vw_sales_overview AS
SELECT
    f.sales_id,
    d.full_date,
    d.year,
    d.month,
    d.day,
    d.month_name,
    d.quarter,
    c.customer_id,
    c.cust_code,
    c.customer_name,
    i.item_id,
    i.item_code,
    i.item_description,
    f.invoice_no,
    f.quantity,
    f.unit_price,
    f.sales_amount,
    f.cost_amount,
    f.profit_amount,
    f.margin_pct,
    f.source_file,
    f.load_timestamp
FROM warehouse.fact_sales_profitability f
INNER JOIN warehouse.dim_date d
    ON d.date_key = f.date_key
INNER JOIN warehouse.dim_customer c
    ON c.customer_id = f.customer_id
INNER JOIN warehouse.dim_item i
    ON i.item_id = f.item_id;