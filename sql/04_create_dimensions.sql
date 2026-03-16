CREATE TABLE warehouse.dim_customer (
    customer_id BIGSERIAL PRIMARY KEY,
    cust_code TEXT NOT NULL UNIQUE,
    customer_name TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE warehouse.dim_item (
    item_id BIGSERIAL PRIMARY KEY,
    item_code TEXT NOT NULL UNIQUE,
    item_description TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE warehouse.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    day INTEGER NOT NULL,
    month_name TEXT NOT NULL,
    quarter INTEGER NOT NULL
);