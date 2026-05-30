CREATE OR REPLACE TABLE revenue_by_product AS
SELECT
    product_id,
    sku,
    post_title,
    price,
    total_sales,
    price * total_sales AS ca
FROM merged_data;

CREATE OR REPLACE TABLE revenue_global AS
SELECT
    ROUND(SUM(ca), 2) AS ca_total
FROM revenue_by_product;