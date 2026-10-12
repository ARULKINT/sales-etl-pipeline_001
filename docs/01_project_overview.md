# 01. Project Overview & Business Case

## Executive Summary
In retail and e-commerce enterprises, sales data is frequently exported from disparate transactional databases, third-party marketplaces, payment gateways, and ERP systems. In raw format, these data dumps are plagued by formatting irregularities, inconsistent date representations, null attributes, invalid quantities, and duplicate records. When business decisions or automated dashboards rely on dirty data, organizations face distorted revenue calculations, inaccurate inventory forecasts, and compromised customer relationship management.

The **Sales Data ETL Pipeline** is an enterprise-grade, lightweight, and resilient Extract-Transform-Load (ETL) framework built in Python and SQL. It ingests messy raw transaction feeds, performs pre-cleaning data profiling, executes strict business transformation rules, enforces data validation assertions, loads normalized records into an indexed analytical database, and generates automated executive business intelligence reports.

---

## Business Problem Statement
Raw transaction exports exhibit critical quality challenges that prevent direct analytics:
1. **Mixed Date Formats:** Dates arrive in varied localized formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`) and occasional unparseable strings, breaking time-series analyses.
2. **Missing Customer Identifiers:** Transactions without identifiable customer accounts cannot be attributed to loyalty tiers or marketing campaigns.
3. **Quantity Inconsistencies:** Negative and zero quantities represent cancelled returns, data transmission glitches, or erroneous test entries that artificially distort sales volume.
4. **Duplicate Entries:** Network retry storms and batch export overlaps generate redundant transaction rows, resulting in inflated revenue counts.
5. **Text Inconsistencies:** Product names and geographical regions have random capitalization (e.g., `MOUSE`, `mouse`, `Mouse`), preventing correct `GROUP BY` aggregations.

---

## Core Objectives
* **Reliability:** Implement a deterministic, repeatable data pipeline that can run unattended on daily or hourly schedules.
* **Data Integrity:** Prevent invalid, incomplete, or corrupted records from entering downstream analytical tables via automated pre-load validation assertions.
* **Auditability:** Record full data lineage and pipeline execution telemetry in an audit table (`etl_pipeline_audit`) tracking run duration, records processed, and retention rates.
* **Actionable Business Intelligence:** Automatically execute analytical queries answering top business questions (product revenue, regional performance, customer lifetime spend, and time trends).
* **Zero Overhead Portability:** Zero external server requirements out of the box using SQLite and SQLAlchemy, while maintaining seamless code portability to enterprise warehouses (PostgreSQL, Snowflake, BigQuery).

---

## Stakeholders & Target Users
* **Data Engineering Teams:** Provides a battle-tested template for modular ETL pipelines with automated testing and CI/CD.
* **Business Intelligence (BI) Analysts:** Guarantees clean, indexed tables ready for direct SQL querying and BI tool integration (Power BI, Tableau, Looker).
* **Executive Leadership:** Automated generation of Markdown and HTML executive summaries delivering instant visibility into revenue, units sold, and top performers.

---

## Key Deliverables
| Deliverable | Description | Location |
| :--- | :--- | :--- |
| **ETL Core Pipeline** | Modular Python pipeline modules covering Extract, Profile, Transform, Validate, Load, Analytics, and Reporting | `src/` |
| **SQL Warehouse & Queries** | Production SQLite schema with analytical indexes and structured analytical SQL queries | `sql/queries.sql`, `data/processed/sales.db` |
| **Executive Reports** | Automated Markdown and HTML summary reports with KPIs and data quality audits | `reports/` |
| **Test Suite** | Comprehensive automated unit, integration, and E2E test suite | `tests/` |
| **Full Documentation Suite** | 10 specialized architecture, setup, data dictionary, and operational guides | `docs/` |
| **Container & CI/CD Assets** | Dockerfile, docker-compose, and GitHub Actions CI workflow | `.github/workflows/ci.yml`, `Dockerfile` |
