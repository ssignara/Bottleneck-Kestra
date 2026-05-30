CREATE OR REPLACE TABLE web_clean AS
WITH ranked_web AS (
    SELECT
        *,
        CAST(sku AS VARCHAR) AS sku_clean,
        ROW_NUMBER() OVER (
            PARTITION BY CAST(sku AS VARCHAR)
            ORDER BY total_sales DESC
        ) AS rn
    FROM web_raw
    WHERE sku IS NOT NULL
      AND total_sales IS NOT NULL
)
SELECT
    sku_clean AS sku,
    total_sales,
    post_title,
    post_type
FROM ranked_web
WHERE rn = 1;