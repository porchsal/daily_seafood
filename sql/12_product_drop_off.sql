CREATE OR REPLACE VIEW mart.vw_product_dropoff_v2 AS
WITH frequent_products AS (
    SELECT
        f.customer_id,
        f.item_id,
        COUNT(*) AS purchase_count
    FROM warehouse.fact_sales_profitability f
    JOIN warehouse.dim_date d ON d.date_key = f.date_key
    WHERE d.full_date >= CURRENT_DATE - INTERVAL '60 days'
    GROUP BY f.customer_id, f.item_id
    HAVING COUNT(*) >= 4
),
last_purchase AS (
    SELECT
        f.customer_id,
        f.item_id,
        MAX(d.full_date) AS last_purchase_date
    FROM warehouse.fact_sales_profitability f
    JOIN warehouse.dim_date d ON d.date_key = f.date_key
    GROUP BY f.customer_id, f.item_id
),
important_customers AS (
    SELECT customer_id
    FROM (
        SELECT
            customer_id,
            SUM(sales_amount) AS total_90d
        FROM warehouse.fact_sales_profitability f
        JOIN warehouse.dim_date d ON d.date_key = f.date_key
        WHERE d.full_date >= CURRENT_DATE - INTERVAL '90 days'
        GROUP BY customer_id
    ) t
    WHERE total_90d >= 3000
)
SELECT
    c.customer_name,
    i.item_description,
    lp.last_purchase_date,
    CURRENT_DATE - lp.last_purchase_date AS days_since_last_purchase,
    CASE
        WHEN CURRENT_DATE - lp.last_purchase_date > 30 THEN '30+ days'
        WHEN CURRENT_DATE - lp.last_purchase_date > 14 THEN '14+ days'
        WHEN CURRENT_DATE - lp.last_purchase_date > 7 THEN '7+ days'
        ELSE 'Active'
    END AS status
FROM last_purchase lp
JOIN frequent_products fp 
    ON fp.customer_id = lp.customer_id AND fp.item_id = lp.item_id
JOIN important_customers ic 
    ON ic.customer_id = lp.customer_id
JOIN warehouse.dim_customer c 
    ON c.customer_id = lp.customer_id
JOIN warehouse.dim_item i 
    ON i.item_id = lp.item_id
WHERE CURRENT_DATE - lp.last_purchase_date > 7;