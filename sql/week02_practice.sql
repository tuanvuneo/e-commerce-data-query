USE ecommerce_dw;


-- 1. Verify table row counts.

SELECT 'dim_customer' AS table_name, COUNT(*) AS row_count
FROM dim_customer

UNION ALL

SELECT 'dim_product', COUNT(*)
FROM dim_product

UNION ALL

SELECT 'dim_location', COUNT(*)
FROM dim_location

UNION ALL

SELECT 'dim_date', COUNT(*)
FROM dim_date

UNION ALL

SELECT 'fact_order_item', COUNT(*)
FROM fact_order_item;


-- 2. Compare item rows with distinct orders.

SELECT
    order_status,
    COUNT(*) AS item_rows,
    COUNT(DISTINCT order_id) AS order_count
FROM fact_order_item
GROUP BY order_status
ORDER BY order_status;


-- 3. Calculate overall completed-sales metrics.

SELECT
    COALESCE(
        SUM(quantity * unit_price - discount_amount),
        0.00
    ) AS net_sales,
    COUNT(DISTINCT order_id) AS completed_orders,
    COALESCE(SUM(quantity), 0) AS units_sold,
    ROUND(
        SUM(quantity * unit_price - discount_amount)
        / NULLIF(COUNT(DISTINCT order_id), 0),
        2
    ) AS average_order_value
FROM fact_order_item
WHERE order_status = 'completed';


-- 4. Calculate monthly completed net sales.

SELECT
    d.calendar_year,
    d.month_number,
    SUM(
        f.quantity * f.unit_price - f.discount_amount
    ) AS net_sales,
    COUNT(DISTINCT f.order_id) AS completed_orders
FROM fact_order_item AS f
JOIN dim_date AS d
    ON f.date_id = d.date_id
WHERE f.order_status = 'completed'
GROUP BY
    d.calendar_year,
    d.month_number
ORDER BY
    d.calendar_year,
    d.month_number;


-- 5. Calculate March completed net sales by state.

SELECT
    l.country,
    l.state_name,
    SUM(
        f.quantity * f.unit_price - f.discount_amount
    ) AS net_sales
FROM fact_order_item AS f
JOIN dim_location AS l
    ON f.location_id = l.location_id
JOIN dim_date AS d
    ON f.date_id = d.date_id
WHERE f.order_status = 'completed'
    AND d.full_date >= '2026-03-01'
    AND d.full_date < '2026-04-01'
GROUP BY
    l.country,
    l.state_name
ORDER BY
    net_sales DESC,
    l.state_name;


-- 6. Calculate completed net sales by brand.

SELECT
    p.brand,
    SUM(
        f.quantity * f.unit_price - f.discount_amount
    ) AS net_sales
FROM fact_order_item AS f
JOIN dim_product AS p
    ON f.product_id = p.product_id
WHERE f.order_status = 'completed'
GROUP BY p.brand
ORDER BY
    net_sales DESC,
    p.brand;


-- 7. Calculate completed net sales by customer gender.

SELECT
    c.gender,
    SUM(
        f.quantity * f.unit_price - f.discount_amount
    ) AS net_sales
FROM fact_order_item AS f
JOIN dim_customer AS c
    ON f.customer_id = c.customer_id
WHERE f.order_status = 'completed'
GROUP BY c.gender
ORDER BY
    net_sales DESC,
    c.gender;


-- 8. Find cities with completed sales.

SELECT
    l.country,
    l.state_name,
    l.city_name,
    SUM(
        f.quantity * f.unit_price - f.discount_amount
    ) AS net_sales
FROM fact_order_item AS f
JOIN dim_location AS l
    ON f.location_id = l.location_id
WHERE f.order_status = 'completed'
GROUP BY
    l.country,
    l.state_name,
    l.city_name
ORDER BY
    net_sales DESC,
    l.city_name;


-- 9. Check that order-level attributes agree across item rows.
-- Expected result: zero rows.

SELECT
    order_id
FROM fact_order_item
GROUP BY order_id
HAVING
    COUNT(DISTINCT customer_id) > 1
    OR COUNT(DISTINCT date_id) > 1
    OR COUNT(DISTINCT location_id) > 1
    OR COUNT(DISTINCT order_status) > 1;