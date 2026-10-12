-- ==============================================================================
-- Sales Data ETL Pipeline — Analytical Queries
-- ==============================================================================

-- Query 1: Top-selling products by revenue
SELECT
    product_name,
    SUM(quantity) AS units_sold,
    ROUND(SUM(total_price), 2) AS total_revenue
FROM sales
GROUP BY product_name
ORDER BY total_revenue DESC
LIMIT 10;

-- Query 2: Monthly sales trend
SELECT
    order_month,
    ROUND(SUM(total_price), 2) AS monthly_revenue,
    COUNT(DISTINCT order_id) AS order_count
FROM sales
GROUP BY order_month
ORDER BY order_month;

-- Query 3: Top customers by spend
SELECT
    customer_id,
    ROUND(SUM(total_price), 2) AS total_spent,
    COUNT(DISTINCT order_id) AS num_orders
FROM sales
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;

-- Query 4: Revenue by region
SELECT
    region,
    ROUND(SUM(total_price), 2) AS total_revenue,
    ROUND(AVG(total_price), 2) AS avg_order_value
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;

-- Query 5: Quarterly performance breakdown
SELECT
    order_quarter,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS units_sold,
    ROUND(SUM(total_price), 2) AS quarterly_revenue
FROM sales
GROUP BY order_quarter
ORDER BY order_quarter;

-- Query 6: Sales volume by day of week
SELECT
    day_of_week,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(total_price), 2) AS day_revenue
FROM sales
GROUP BY day_of_week
ORDER BY day_revenue DESC;
