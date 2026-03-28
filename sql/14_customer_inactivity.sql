CREATE OR REPLACE VIEW mart.vw_customer_inactivity AS
SELECT
    c.customer_id,
    c.cust_code,
    c.customer_name,
    MAX(d.full_date) AS last_order_date,
    CURRENT_DATE - MAX(d.full_date) AS days_since_last_order,
    COUNT(DISTINCT f.invoice_no) AS invoice_count,
    SUM(f.sales_amount) AS total_sales,
    SUM(f.profit_amount) AS total_profit,
    CASE
        WHEN CURRENT_DATE - MAX(d.full_date) > 60 THEN 'Inactive'
        WHEN CURRENT_DATE - MAX(d.full_date) > 30 THEN 'At Risk'
        ELSE 'Active'
    END AS customer_status
FROM warehouse.fact_sales_profitability f
INNER JOIN warehouse.dim_customer c
    ON c.customer_id = f.customer_id
INNER JOIN warehouse.dim_date d
    ON d.date_key = f.date_key
GROUP BY
    c.customer_id,
    c.cust_code,
    c.customer_name;