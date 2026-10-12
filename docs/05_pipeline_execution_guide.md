# 05. Pipeline Execution & Operations Guide

This guide details how to execute, configure, and monitor the Sales ETL Pipeline in development and production environments.

---

## 1. Quick Start Execution

Run the complete pipeline end-to-end with default parameters:
```bash
python src/main.py
```

### What Happens During Default Execution:
1. **Stage 1 (Extract):** Reads `data/raw/sales_data.csv`.
2. **Stage 2 (Profile):** Analyzes raw quality metrics and prints a data health summary.
3. **Stage 3 (Transform):** Cleans dates, standardizes product names, drops missing IDs/quantities, removes invalid entries, deduplicates, and enriches columns.
4. **Stage 4 (Validate):** Asserts all 8 quality rules.
5. **Stage 5 (Load):** Ingests clean records into `data/processed/sales.db`, creates analytical indexes, and writes to `etl_pipeline_audit`.
6. **Stage 6 (Analytics):** Runs all 6 analytical queries from `sql/queries.sql`, calculates executive KPIs, and exports CSV result sets to `data/processed/analytics_exports/`.
7. **Stage 7 (Report):** Writes Executive and Data Quality reports to `reports/pipeline_execution_report.md` and `reports/pipeline_execution_report.html`.

---

## 2. Command-Line Options (CLI)

The pipeline orchestrator provides flexible command-line flags:

```bash
python src/main.py [OPTIONS]
```

| Flag | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `--input` | `STRING` | `data/raw/sales_data.csv` | Custom path to an input raw CSV file |
| `--db` | `STRING` | `data/processed/sales.db` | Custom output path for target SQLite database |
| `--skip-analytics` | `FLAG` | `False` | Skips executing SQL queries and KPI computations |
| `--no-report` | `FLAG` | `False` | Disables writing Markdown and HTML report files |
| `--verbose` | `FLAG` | `False` | Enables detailed DEBUG level logging |

### Example CLI Scenarios

#### Run with Custom Source & Target
```bash
python src/main.py --input /data/incoming/october_sales.csv --db /data/warehouse/october_warehouse.db
```

#### Fast Ingestion Mode (Skip Analytics & Reporting)
Useful in automated ingestion loops when only data loading is required:
```bash
python src/main.py --skip-analytics --no-report
```

#### Verbose Debugging
Displays individual step timers, SQL execution logs, and encoding detection:
```bash
python src/main.py --verbose
```

---

## 3. Log Output & Monitoring

The pipeline automatically logs all execution telemetry to two destinations simultaneously:
1. **Standard Output (Console):** Color-coded and formatted summary stream.
2. **Persistent Log File:** Stored in `pipeline.log` using UTF-8 encoding.

### Sample Console Log
```text
2026-10-12 06:50:59,902 | INFO    | === ETL PIPELINE STARTED [Run ID: d84fa264] ===
2026-10-12 06:50:59,902 | INFO    | Source file: C:\drive g\Projects_july\sales-etl-pipeline\data\raw\sales_data.csv
2026-10-12 06:50:59,902 | INFO    | Target database: C:\drive g\Projects_july\sales-etl-pipeline\data\processed\sales.db
2026-10-12 06:50:59,902 | INFO    | Stage 1/7: Extracting raw data...
2026-10-12 06:50:59,905 | INFO    | Extracted 508 rows and 7 columns from 'sales_data.csv' (25.7 KB)
2026-10-12 06:50:59,905 | INFO    | Stage 2/7: Profiling raw data quality...
============================================================
DATA PROFILING REPORT: Raw Data Profile
============================================================
Rows: 508 | Columns: 7
Duplicate Rows: 8 | Duplicate Orders: 8
Negative Quantities: 5 | Zero Quantities: 0
------------------------------------------------------------
Null Values per Column:
  * quantity       : [MISSING: 10 (1.97%)]
  * customer_id    : [MISSING: 15 (2.95%)]
============================================================
2026-10-12 06:50:59,910 | INFO    | Stage 3/7: Transforming and cleaning records...
2026-10-12 06:50:59,916 | INFO    | Dropped 23 rows with missing mandatory fields
2026-10-12 06:50:59,917 | INFO    | Dropped 5 rows with non-positive quantity
2026-10-12 06:50:59,919 | INFO    | Dropped 8 duplicate rows
2026-10-12 06:50:59,923 | INFO    | Stage 4/7: Running data validation assertions...
2026-10-12 06:50:59,926 | INFO    | [VALIDATION PASSED] All 8 assertions passed successfully on 472 records.
2026-10-12 06:50:59,926 | INFO    | Stage 5/7: Loading data into SQLite database...
2026-10-12 06:50:59,992 | INFO    | Loaded 472 rows into table 'sales'
2026-10-12 06:51:00,032 | INFO    | Database indexes verified on table 'sales'
2026-10-12 06:51:00,035 | INFO    | Stage 6/7: Executing SQL analytical queries...
2026-10-12 06:51:00,058 | INFO    | Executive KPIs computed: Total Revenue = $1,551,446.76
2026-10-12 06:51:00,062 | INFO    | Stage 7/7: Compiling Executive and Data Quality Reports...
2026-10-12 06:51:00,079 | INFO    | Audit log saved: Run ID 'd84fa264' [SUCCESS] in 0.16s
2026-10-12 06:51:00,079 | INFO    | === PIPELINE COMPLETED SUCCESSFULLY IN 0.16s ===

============================================================
PIPELINE RUN SUMMARY: SUCCESS [Run ID: d84fa264]
Raw Input: 508 | Clean Loaded: 472 | Dropped: 36
Retention Rate: 92.91% | Duration: 0.16s
Total Revenue: $1,551,446.76 | Orders: 472
============================================================
```

---

## 4. Querying the Processed Database

To query the database directly in Python or terminal:

```bash
python -c "import sqlite3; conn = sqlite3.connect('data/processed/sales.db'); print(conn.execute('SELECT COUNT(*) FROM sales').fetchone())"
```

To run interactive SQL, open `data/processed/sales.db` using:
* [DB Browser for SQLite](https://sqlitebrowser.org/) (GUI)
* VS Code Extension: `SQLite Viewer` or `SQLTools`
* SQLite CLI: `sqlite3 data/processed/sales.db`
