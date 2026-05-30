CREATE OR REPLACE TABLE merged_data AS
SELECT
    e.product_id,
    l.sku,
    w.post_title,
    e.price,
    w.total_sales,
    e.stock_quantity,
    e.stock_status
FROM erp_clean e
INNER JOIN liaison_clean l
    ON e.product_id = l.product_id
INNER JOIN web_clean w
    ON l.sku = w.sku;