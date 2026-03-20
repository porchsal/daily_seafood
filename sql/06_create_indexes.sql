CREATE INDEX idx_staging_cip_invoice_date
    ON staging.customer_item_profitability(invoice_date);

CREATE INDEX idx_staging_cip_invoice_no
    ON staging.customer_item_profitability(invoice_no);

CREATE INDEX idx_staging_cip_cust_code
    ON staging.customer_item_profitability(cust_code);

CREATE INDEX idx_staging_cip_item_code
    ON staging.customer_item_profitability(item_code);

CREATE INDEX idx_fact_sales_date_key
    ON warehouse.fact_sales_profitability(date_key);

CREATE INDEX idx_fact_sales_customer_id
    ON warehouse.fact_sales_profitability(customer_id);

CREATE INDEX idx_fact_sales_item_id
    ON warehouse.fact_sales_profitability(item_id);

CREATE INDEX idx_fact_sales_invoice_no
    ON warehouse.fact_sales_profitability(invoice_no);

-- ALTER TABLE warehouse.fact_sales_profitability
-- ADD CONSTRAINT uq_fact_sales_line
-- UNIQUE (date_key, customer_id, item_id, invoice_no, sales_amount); constraint need to be investigated further, as it is not working as expected, and allowing duplicates in the fact table.