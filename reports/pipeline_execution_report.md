# Sales ETL Pipeline — Executive & Data Quality Report

> **Run ID:** `6a11b9d1` | **Generated:** `2026-10-12 07:07:31` | **Execution Time:** `0.16s` | **Status:** `SUCCESS`

## 1. Executive Business KPIs
| Metric | Value | Business Description |
| :--- | :--- | :--- |
| **Total Revenue** | **$1,551,446.76** | Cumulative gross sales across cleaned transactions |
| **Total Orders** | **472** | Total distinct validated orders processed |
| **Active Customers** | **40** | Unique customer accounts with completed purchases |
| **Total Units Sold** | **2,574** | Physical products shipped |
| **Average Order Value (AOV)** | **$3,286.96** | Mean revenue generated per transaction |
| **Top Product by Revenue** | **Mouse** ($271,851.41) | Highest grossing merchandise |
| **Top Region by Revenue** | **South** ($448,035.22) | Primary regional revenue driver |

## 2. Data Cleaning & Integrity Audit
| Pipeline Stage | Metric | Count / Value | Impact / Rule |
| :--- | :--- | :--- | :--- |
| **Extract** | Raw Input Rows | 508 | Extracted from raw CSV source |
| **Profiling** | Raw Missing Fields | 25 cells | Unattributed customer IDs & missing quantities |
| **Profiling** | Raw Duplicate Rows | 8 rows | Repeated transaction submissions |
| **Profiling** | Raw Anomaly Quantities | 5 rows | Non-positive / negative values |
| **Transform** | Total Rows Dropped | 36 rows | Dropped corrupted, unparseable, or duplicate data |
| **Validate** | Final Clean Rows | 472 rows | Passed all 8 strict data validation assertions |
| **Quality Score** | Data Retention Rate | **92.91%** | Safe, reliable data loading threshold |

## 3. SQL Analytics Findings
### Query 1: Top-selling products by revenue
| product_name | units_sold | total_revenue |
| --- | --- | --- |
| Mouse | 424 | 271,851.41 |
| Headset | 374 | 251,031.36 |
| Keyboard | 357 | 217,939.47 |
| USB Cable | 313 | 189,134.43 |
| Webcam | 293 | 183,682.25 |
| Laptop | 317 | 172,946.91 |
| Desk Chair | 257 | 138,450.89 |
| Monitor | 239 | 126,410.04 |

### Query 2: Monthly sales trend
| order_month | monthly_revenue | order_count |
| --- | --- | --- |
| 2024-01 | 173,689.24 | 41 |
| 2024-02 | 105,952.19 | 36 |
| 2024-03 | 134,028.88 | 40 |
| 2024-04 | 106,548.70 | 33 |
| 2024-05 | 83,099.98 | 32 |
| 2024-06 | 94,143.62 | 35 |
| 2024-07 | 163,692.04 | 43 |
| 2024-08 | 119,923.71 | 46 |
| 2024-09 | 157,569.97 | 39 |
| 2024-10 | 129,979.58 | 37 |
| 2024-11 | 115,808.84 | 41 |
| 2024-12 | 167,010.01 | 49 |

### Query 3: Top customers by spend
| customer_id | total_spent | num_orders |
| --- | --- | --- |
| CUST036 | 87,027.21 | 21 |
| CUST027 | 70,758.04 | 16 |
| CUST013 | 58,771.25 | 14 |
| CUST002 | 58,615.90 | 13 |
| CUST010 | 55,684.98 | 13 |
| CUST032 | 53,873.08 | 18 |
| CUST015 | 51,829.88 | 13 |
| CUST033 | 50,437.44 | 15 |
| CUST021 | 49,884.75 | 17 |
| CUST007 | 49,435.66 | 15 |

### Query 4: Revenue by region
| region | total_revenue | avg_order_value |
| --- | --- | --- |
| South | 448,035.22 | 3,446.42 |
| West | 396,888.72 | 3,481.48 |
| North | 365,515.04 | 2,996.02 |
| East | 341,007.78 | 3,217.05 |

### Query 5: Quarterly performance breakdown
| order_quarter | total_orders | units_sold | quarterly_revenue |
| --- | --- | --- | --- |
| 2024Q1 | 117 | 654 | 413,670.31 |
| 2024Q2 | 100 | 495 | 283,792.30 |
| 2024Q3 | 128 | 704 | 441,185.72 |
| 2024Q4 | 127 | 721 | 412,798.43 |

### Query 6: Sales volume by day of week
| day_of_week | order_count | day_revenue |
| --- | --- | --- |
| Monday | 76 | 238,320.43 |
| Wednesday | 67 | 238,041.30 |
| Friday | 71 | 228,984.12 |
| Sunday | 68 | 220,850.32 |
| Saturday | 66 | 219,650.03 |
| Thursday | 65 | 215,718.32 |
| Tuesday | 59 | 189,882.24 |

## 4. Strategic Business Insights
- **Product Focus:** `Mouse` is leading sales volume. Consider inventory prioritization and targeted bundling.
- **Regional Growth:** `South` accounts for the highest regional revenue share. Explore regional promotion strategies for lower-volume territories.
- **Data Quality Assurance:** 36 erroneous records were prevented from entering the analytics warehouse, ensuring reporting integrity.

---
*Report automatically compiled by the Sales Data ETL Pipeline.*