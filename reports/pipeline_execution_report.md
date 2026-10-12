# Sales ETL Pipeline — Executive & Data Quality Report

> **Run ID:** `fe4d588e` | **Generated:** `2026-10-12 15:11:12` | **Execution Time:** `0.13s` | **Status:** `SUCCESS`

## 1. Executive Business KPIs
| Metric | Value | Business Description |
| :--- | :--- | :--- |
| **Total Revenue** | **$2,500.00** | Cumulative gross sales across cleaned transactions |
| **Total Orders** | **2** | Total distinct validated orders processed |
| **Active Customers** | **2** | Unique customer accounts with completed purchases |
| **Total Units Sold** | **6** | Physical products shipped |
| **Average Order Value (AOV)** | **$1,250.00** | Mean revenue generated per transaction |
| **Top Product by Revenue** | **Laptop** ($2,400.00) | Highest grossing merchandise |
| **Top Region by Revenue** | **North** ($2,400.00) | Primary regional revenue driver |

## 2. Data Cleaning & Integrity Audit
| Pipeline Stage | Metric | Count / Value | Impact / Rule |
| :--- | :--- | :--- | :--- |
| **Extract** | Raw Input Rows | 5 | Extracted from raw CSV source |
| **Profiling** | Raw Missing Fields | 1 cells | Unattributed customer IDs & missing quantities |
| **Profiling** | Raw Duplicate Rows | 1 rows | Repeated transaction submissions |
| **Profiling** | Raw Anomaly Quantities | 1 rows | Non-positive / negative values |
| **Transform** | Total Rows Dropped | 3 rows | Dropped corrupted, unparseable, or duplicate data |
| **Validate** | Final Clean Rows | 2 rows | Passed all 8 strict data validation assertions |
| **Quality Score** | Data Retention Rate | **40.0%** | Safe, reliable data loading threshold |

## 3. SQL Analytics Findings
### Query 1: Top-selling products by revenue
| product_name | units_sold | total_revenue |
| --- | --- | --- |
| Laptop | 2 | 2,400.00 |
| USB Cable | 4 | 100.00 |

### Query 2: Monthly sales trend
| order_month | monthly_revenue | order_count |
| --- | --- | --- |
| 2024-01 | 2,400.00 | 1 |
| 2024-03 | 100.00 | 1 |

### Query 3: Top customers by spend
| customer_id | total_spent | num_orders |
| --- | --- | --- |
| CUST001 | 2,400.00 | 1 |
| CUST004 | 100.00 | 1 |

### Query 4: Revenue by region
| region | total_revenue | avg_order_value |
| --- | --- | --- |
| North | 2,400.00 | 2,400.00 |
| West | 100.00 | 100.00 |

### Query 5: Quarterly performance breakdown
| order_quarter | total_orders | units_sold | quarterly_revenue |
| --- | --- | --- | --- |
| 2024Q1 | 2 | 6 | 2,500.00 |

### Query 6: Sales volume by day of week
| day_of_week | order_count | day_revenue |
| --- | --- | --- |
| Monday | 1 | 2,400.00 |
| Friday | 1 | 100.00 |

## 4. Strategic Business Insights
- **Product Focus:** `Laptop` is leading sales volume. Consider inventory prioritization and targeted bundling.
- **Regional Growth:** `North` accounts for the highest regional revenue share. Explore regional promotion strategies for lower-volume territories.
- **Data Quality Assurance:** 3 erroneous records were prevented from entering the analytics warehouse, ensuring reporting integrity.

---
*Report automatically compiled by the Sales Data ETL Pipeline.*