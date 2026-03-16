CREATE VIEW mart.vw_staging_customer_item_profitability AS
SELECT
    cust_code,
    customer_name,
    item_code,
    item_description,
    invoice_date,
    invoice_no,
    quantity,
    price,
    cost,
    profit,
    margin,
    source_file,
    created_at
FROM staging.customer_item_profitability;