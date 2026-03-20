CREATE OR REPLACE VIEW mart.vw_all_customers_lost AS
SELECT
    c.customer_name,
    MAX(d.full_date) AS last_order_date,
    CURRENT_DATE - MAX(d.full_date) AS days_since_last_order,
    SUM(f.sales_amount) AS total_sales
FROM warehouse.fact_sales_profitability f
JOIN warehouse.dim_customer c ON c.customer_id = f.customer_id
JOIN warehouse.dim_date d ON d.date_key = f.date_key
GROUP BY c.customer_name
HAVING CURRENT_DATE - MAX(d.full_date) > 14
ORDER BY total_sales DESC;