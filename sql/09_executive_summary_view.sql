CREATE OR REPLACE VIEW mart.vw_executive_summary AS
WITH base AS (
    SELECT
        d.full_date,
        f.sales_amount
    FROM warehouse.fact_sales_profitability f
    JOIN warehouse.dim_date d ON d.date_key = f.date_key
),
today AS (
    SELECT SUM(sales_amount) AS sales_today
    FROM base
    WHERE full_date = CURRENT_DATE
),
wtd AS (
    SELECT SUM(sales_amount) AS sales_wtd
    FROM base
    WHERE full_date >= date_trunc('week', CURRENT_DATE)
),
mtd AS (
    SELECT SUM(sales_amount) AS sales_mtd
    FROM base
    WHERE full_date >= date_trunc('month', CURRENT_DATE)
),
ytd AS (
    SELECT SUM(sales_amount) AS sales_ytd
    FROM base
    WHERE full_date >= date_trunc('year', CURRENT_DATE)
)
SELECT *
FROM today, wtd, mtd, ytd;