# 03. Data Dictionary & Schema Specification

This document details the schema definitions, data types, constraints, and business rules for all data assets throughout the pipeline lifecycle.

---

## 1. Raw Ingestion Schema (`data/raw/sales_data.csv`)

The raw transaction export represents point-of-sale data before validation or cleaning.

| Column Name | Raw Data Type | Nullable | Example Values | Description |
| :--- | :--- | :--- | :--- | :--- |
| `order_id` | `VARCHAR` | No | `ORD0001`, `ORD0042` | Unique transaction identifier |
| `order_date` | `VARCHAR` | No | `03-12-2024`, `2024-07-13`, `26/10/2024` | Mixed date format string |
| `product_name` | `VARCHAR` | No | `MOUSE`, `usb cable`, `Laptop` | Product name with inconsistent casing |
| `quantity` | `FLOAT` / `VARCHAR` | Yes | `5.0`, `-1.0`, `NaN` | Units ordered; can contain negatives and nulls |
| `unit_price` | `FLOAT` | No | `297.65`, `1195.37` | Base price per product unit in USD |
| `customer_id` | `VARCHAR` | Yes | `CUST007`, `CUST028`, `NaN` | Customer account identifier; can contain nulls |
| `region` | `VARCHAR` | No | `North`, `south`, `West` | Geographical sales region |

---

## 2. Processed Warehouse Schema (`sales` Table in SQLite & MySQL)

Normalized, validated, and enriched transactional records loaded into the analytics database.
By default, the pipeline persists to local SQLite (`data/processed/sales.db`). When configured for MySQL (`DB_CONNECTION_URL="mysql+pymysql://..."`), SQLAlchemy maps columns to the equivalent MySQL enterprise types shown below:

| Column Name | SQLite Type | MySQL / Postgres Type | Python Type | Primary Key | Nullable | Constraints & Rules | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `order_id` | `TEXT` | `VARCHAR(32)` | `str` | Yes (Unique) | No | Format: `^ORD\d{4}$` | Unique identifier for each transaction |
| `order_date` | `TEXT` | `DATE` / `VARCHAR(10)` | `str` | No | No | Format: `YYYY-MM-DD` | Standardized ISO 8601 transaction date |
| `product_name` | `TEXT` | `VARCHAR(100)` | `str` | No | No | Clean Title Case + Acronyms | Standardized product category |
| `quantity` | `INTEGER` | `INT` | `int64` | No | No | `quantity >= 1` | Verified positive unit count |
| `unit_price` | `REAL` | `DECIMAL(10,2)` | `float64` | No | No | `unit_price > 0.0` | Unit price in USD (2 decimals) |
| `customer_id` | `TEXT` | `VARCHAR(32)` | `str` | No | No | Format: `^CUST\d{3}$` | Attributed customer identifier |
| `region` | `TEXT` | `VARCHAR(50)` | `str` | No | No | Title Case (`North`, `South`, `East`, `West`) | Validated geographic zone |
| `total_price` | `REAL` | `DECIMAL(10,2)` | `float64` | No | No | `ROUND(quantity * unit_price, 2)` | Total transaction gross amount in USD |
| `order_month` | `TEXT` | `VARCHAR(7)` | `str` | No | No | Format: `YYYY-MM` | Month grouping for trend analysis |
| `order_year` | `INTEGER` | `INT` | `int64` | No | No | `2000 <= order_year <= 2099` | Transaction calendar year |
| `order_quarter` | `TEXT` | `VARCHAR(8)` | `str` | No | No | Format: `YYYY-Q#` (e.g., `2024-Q1`) | Fiscal quarter grouping |
| `day_of_week` | `TEXT` | `VARCHAR(15)` | `str` | No | No | `Monday` .. `Sunday` | Day of week for purchasing cycle analysis |

### Database Indexes

To ensure sub-millisecond query performance on analytical workloads, the following B-tree indexes are maintained on `sales`:

* `idx_sales_order_date` on `(order_date)` — Optimizes date-range filters and monthly time-series queries.
* `idx_sales_customer_id` on `(customer_id)` — Accelerates customer lifetime value and aggregation queries.
* `idx_sales_product_name` on `(product_name)` — Accelerates product revenue rankings and volume groupings.
* `idx_sales_region` on `(region)` — Optimizes regional revenue and geographic breakdown queries.

---

## 3. Pipeline Audit Schema (`etl_pipeline_audit` Table)

Stores operational telemetry, audit trails, and execution lineage for monitoring and governance.

| Column Name | SQL Type | Description |
| :--- | :--- | :--- |
| `run_id` | `TEXT PRIMARY KEY` | Unique 8-character execution identifier (e.g., `d84fa264`) |
| `run_timestamp` | `TEXT` | UTC timestamp of pipeline execution (`YYYY-MM-DD HH:MM:SS`) |
| `status` | `TEXT` | Final outcome (`SUCCESS` or `FAILED`) |
| `raw_rows` | `INTEGER` | Number of rows extracted from the source files |
| `clean_rows` | `INTEGER` | Number of validated rows loaded into `sales` |
| `dropped_rows` | `INTEGER` | Number of dirty/corrupted rows eliminated |
| `duration_sec` | `REAL` | Total end-to-end execution duration in seconds |
| `notes` | `TEXT` | Summary details and data retention rate |

---

## 4. Product Catalog Reference

Standardized product categories recognized by the pipeline:

| Product Name | Category | Base Unit Price Range (USD) |
| :--- | :--- | :--- |
| **Desk Chair** | Office Furniture | $50.00 – $1,200.00 |
| **Headset** | Audio Peripherals | $25.00 – $1,000.00 |
| **Keyboard** | Input Devices | $20.00 – $1,200.00 |
| **Laptop** | Computing Hardware | $300.00 – $1,200.00 |
| **Monitor** | Displays | $150.00 – $1,200.00 |
| **Mouse** | Input Devices | $10.00 – $1,000.00 |
| **USB Cable** | Connectivity Accessories | $5.00 – $1,200.00 |
| **Webcam** | Video Peripherals | $30.00 – $1,000.00 |
