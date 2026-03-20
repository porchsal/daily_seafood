CREATE OR REPLACE VIEW mart.vw_important_customers_lost AS
WITH last_90_days AS (
    SELECT
        f.customer_id,
        SUM(f.sales_amount) AS total_90d
    FROM warehouse.fact_sales_profitability f
    JOIN warehouse.dim_date d ON d.date_key = f.date_key
    WHERE d.full_date >= CURRENT_DATE - INTERVAL '90 days'
    GROUP BY f.customer_id
),
important_customers AS (
    SELECT customer_id
    FROM last_90_days
    WHERE total_90d >= 3000
),
last_order AS (
    SELECT
        f.customer_id,
        MAX(d.full_date) AS last_order_date
    FROM warehouse.fact_sales_profitability f
    JOIN warehouse.dim_date d ON d.date_key = f.date_key
    GROUP BY f.customer_id
)
SELECT
    c.customer_name,
    lo.last_order_date,
    CURRENT_DATE - lo.last_order_date AS days_since_last_order,
    CASE
        WHEN CURRENT_DATE - lo.last_order_date > 30 THEN '30+ days'
        WHEN CURRENT_DATE - lo.last_order_date > 14 THEN '14+ days'
        WHEN CURRENT_DATE - lo.last_order_date > 7 THEN '7+ days'
        ELSE 'Active'
    END AS status
FROM last_order lo
JOIN important_customers ic ON ic.customer_id = lo.customer_id
JOIN warehouse.dim_customer c ON c.customer_id = lo.customer_id
WHERE CURRENT_DATE - lo.last_order_date > 7;