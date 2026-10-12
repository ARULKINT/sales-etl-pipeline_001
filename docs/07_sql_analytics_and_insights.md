# 07. SQL Analytics & Business Insights

This document reviews the analytical SQL queries executed by the pipeline against the processed warehouse, including actual output datasets and business interpretations.

---

## Analytical Queries Overview

The pipeline executes 6 core analytical queries defined in `sql/queries.sql`:
1. **Top-Selling Products by Revenue:** Identifies revenue drivers and unit velocity.
2. **Monthly Sales Trend:** Tracks month-over-month revenue and order volumes.
3. **Top Customers by Lifetime Spend:** Identifies high-value VIP accounts.
4. **Revenue by Geographic Region:** Compares market penetration and average order values.
5. **Quarterly Performance Breakdown:** Measures seasonal cyclicality.
6. **Sales Volume by Day of Week:** Pinpoints customer purchasing patterns across the weekly cycle.

---

## Query 1: Top-Selling Products by Revenue

### Business Question
*Which products generate the highest cumulative gross sales, and which move the most physical volume?*

### SQL Syntax
```sql
SELECT
    product_name,
    SUM(quantity) AS units_sold,
    ROUND(SUM(total_price), 2) AS total_revenue
FROM sales
GROUP BY product_name
ORDER BY total_revenue DESC
LIMIT 10;
```

### Empirical Results
| Product Name | Units Sold | Total Revenue (USD) | Revenue Share |
| :--- | :--- | :--- | :--- |
| **Mouse** | 361 | $237,841.92 | 15.3% |
| **Headset** | 331 | $228,793.91 | 14.7% |
| **Keyboard** | 329 | $221,411.39 | 14.3% |
| **Desk Chair** | 344 | $215,925.32 | 13.9% |
| **Monitor** | 309 | $193,762.62 | 12.5% |
| **USB Cable** | 316 | $161,289.44 | 10.4% |
| **Webcam** | 290 | $150,711.08 | 9.7% |
| **Laptop** | 294 | $141,711.08 | 9.1% |

### Strategic Insight
Peripherals (Mice, Headsets, Keyboards) account for over 44% of total revenue. High unit volume in lower-priced accessories significantly outpaces high-ticket hardware like Laptops in aggregate gross margin.

---

## Query 2: Monthly Sales Trend

### Business Question
*How is company revenue trending across the calendar year, and is order velocity expanding?*

### SQL Syntax
```sql
SELECT
    order_month,
    ROUND(SUM(total_price), 2) AS monthly_revenue,
    COUNT(DISTINCT order_id) AS order_count
FROM sales
GROUP BY order_month
ORDER BY order_month;
```

### Empirical Results
| Month | Monthly Revenue (USD) | Order Count | Avg Order Value (USD) |
| :--- | :--- | :--- | :--- |
| **2024-01** | $173,689.24 | 41 | $4,236.32 |
| **2024-02** | $105,952.19 | 36 | $2,943.12 |
| **2024-03** | $134,028.88 | 40 | $3,350.72 |
| **2024-04** | $106,548.70 | 33 | $3,228.75 |
| **2024-05** | $83,099.98 | 32 | $2,596.87 |
| **2024-06** | $94,143.62 | 35 | $2,689.82 |
| **2024-07** | $163,692.04 | 43 | $3,806.79 |
| **2024-08** | $119,923.71 | 46 | $2,607.04 |
| **2024-09** | $157,569.97 | 39 | $4,040.26 |
| **2024-10** | $129,979.58 | 37 | $3,512.96 |
| **2024-11** | $115,808.84 | 41 | $2,824.61 |
| **2024-12** | $167,010.01 | 49 | $3,408.37 |

### Strategic Insight
Peak revenue occurs in January ($173.7K), July ($163.7K), September ($157.6K), and December ($167.0K), demonstrating mid-year and holiday purchasing surges. May experienced the lowest seasonal dip ($83.1K).

---

## Query 3: Top Customers by Lifetime Spend

### Business Question
*Who are our top 10 most valuable accounts, and how frequently do they place orders?*

### SQL Syntax
```sql
SELECT
    customer_id,
    ROUND(SUM(total_price), 2) AS total_spent,
    COUNT(DISTINCT order_id) AS num_orders
FROM sales
GROUP BY customer_id
ORDER BY total_spent DESC
LIMIT 10;
```

### Empirical Results
| Customer ID | Total Spend (USD) | Number of Orders | Avg Spend per Order |
| :--- | :--- | :--- | :--- |
| **CUST004** | $66,698.81 | 18 | $3,705.49 |
| **CUST036** | $64,310.87 | 15 | $4,287.39 |
| **CUST009** | $57,010.15 | 16 | $3,563.13 |
| **CUST020** | $54,923.72 | 15 | $3,661.58 |
| **CUST039** | $53,745.02 | 15 | $3,583.00 |
| **CUST018** | $53,230.12 | 16 | $3,326.88 |
| **CUST028** | $52,940.83 | 16 | $3,308.80 |
| **CUST013** | $51,460.29 | 15 | $3,430.69 |
| **CUST023** | $49,850.11 | 15 | $3,323.34 |
| **CUST032** | $48,720.94 | 14 | $3,480.07 |

### Strategic Insight
Customer `CUST004` leads all accounts with $66,698.81 across 18 transactions. The top 10 accounts contribute over $552,000 (over 35% of company revenue), highlighting the necessity of a dedicated B2B Key Account Manager program.

---

## Query 4: Revenue by Geographic Region

### Business Question
*Which regional territories produce the highest revenue, and what is the regional Average Order Value (AOV)?*

### SQL Syntax
```sql
SELECT
    region,
    ROUND(SUM(total_price), 2) AS total_revenue,
    ROUND(AVG(total_price), 2) AS avg_order_value
FROM sales
GROUP BY region
ORDER BY total_revenue DESC;
```

### Empirical Results
| Region | Total Revenue (USD) | Average Order Value (AOV) | Transaction Share |
| :--- | :--- | :--- | :--- |
| **South** | $448,035.22 | $3,420.12 | 27.8% |
| **North** | $401,234.89 | $3,343.62 | 25.4% |
| **East** | $378,540.11 | $3,235.39 | 24.8% |
| **West** | $323,636.54 | $3,142.10 | 22.0% |

### Strategic Insight
The **South** region leads revenue and AOV ($3,420.12). The **West** region lags behind with $323.6K in gross revenue and lower AOV. Regional campaigns should aim to expand sales in the Western region.

---

## Query 5: Quarterly Performance Breakdown

### SQL Syntax
```sql
SELECT
    order_quarter,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS units_sold,
    ROUND(SUM(total_price), 2) AS quarterly_revenue
FROM sales
GROUP BY order_quarter
ORDER BY order_quarter;
```

### Empirical Results
| Quarter | Total Orders | Units Sold | Quarterly Revenue (USD) |
| :--- | :--- | :--- | :--- |
| **2024-Q1** | 117 | 640 | $413,670.31 |
| **2024-Q2** | 100 | 542 | $283,792.30 |
| **2024-Q3** | 128 | 702 | $441,185.72 |
| **2024-Q4** | 127 | 690 | $412,798.43 |

---

## Query 6: Sales Volume by Day of Week

### SQL Syntax
```sql
SELECT
    day_of_week,
    COUNT(DISTINCT order_id) AS order_count,
    ROUND(SUM(total_price), 2) AS day_revenue
FROM sales
GROUP BY day_of_week
ORDER BY day_revenue DESC;
```

### Empirical Results
| Day of Week | Order Count | Revenue (USD) |
| :--- | :--- | :--- |
| **Tuesday** | 74 | $256,410.22 |
| **Thursday** | 72 | $244,190.54 |
| **Monday** | 70 | $238,912.01 |
| **Wednesday** | 68 | $229,045.19 |
| **Friday** | 66 | $215,820.40 |
| **Saturday** | 62 | $191,320.11 |
| **Sunday** | 60 | $175,748.29 |

### Strategic Insight
Mid-week business days (Tuesday and Thursday) account for the highest ordering activity, characteristic of B2B procurement patterns. Weekend purchasing decreases by ~30%.
