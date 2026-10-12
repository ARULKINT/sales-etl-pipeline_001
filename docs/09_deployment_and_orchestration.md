# 09. Deployment & Orchestration Guide

This guide details how to deploy, schedule, containerize, and scale the Sales ETL Pipeline into automated operational environments.

---

## 1. Local & On-Premises Scheduling

### Option A: Windows Task Scheduler
To schedule the pipeline to run automatically every night at 02:00 AM on Windows:

1. Open **Task Scheduler** (`taskschd.msc`).
2. Click **Create Basic Task** -> Name it `DailySalesETLPipeline`.
3. Set the trigger to **Daily** at `02:00:00`.
4. Set Action to **Start a Program**:
   * **Program/script:** `powershell.exe`
   * **Add arguments:** `-ExecutionPolicy Bypass -File "C:\drive g\Projects_july\sales-etl-pipeline\run_pipeline.ps1"`
   * **Start in:** `C:\drive g\Projects_july\sales-etl-pipeline\`
5. Check **Run whether user is logged on or not**.

### Option B: Linux / macOS Crontab
To run daily at 02:00 AM on Unix systems:

```bash
crontab -e
```

Add the following entry:
```cron
0 2 * * * cd /opt/sales-etl-pipeline && ./venv/bin/python src/main.py >> /var/log/sales_etl.log 2>&1
```

---

## 2. Containerized Deployment (Docker)

The project includes production-ready containerization files:
* `Dockerfile`
* `docker-compose.yml`

### Building the Docker Image
```bash
docker build -t sales-etl-pipeline:latest .
```

### Running the Containerized Pipeline
```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/reports:/app/reports \
  -v $(pwd)/logs:/app/logs \
  sales-etl-pipeline:latest
```

### Using Docker Compose
```bash
docker-compose up --build
```
This executes the pipeline inside an isolated Python Linux container, persisting output databases, reports, and logs to your local host directories.

---

## 3. Workflow Orchestration with Apache Airflow

For enterprise data platforms, wrap the pipeline in an Apache Airflow DAG:

```python
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'data_engineering',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['data-alerts@example.com'],
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'sales_etl_daily_pipeline',
    default_args=default_args,
    description='Automated Daily Sales ETL Ingestion and Reporting',
    schedule_interval='0 2 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['sales', 'etl', 'reporting'],
) as dag:

    run_etl = BashOperator(
        task_id='execute_sales_etl',
        bash_command='cd /opt/sales-etl-pipeline && python src/main.py --generate-report',
    )

    run_etl
```

---

## 4. Enterprise Cloud Migration Blueprint

The pipeline is intentionally decoupled via SQLAlchemy and Pandas, making cloud warehousing migrations straightforward:

| Component | Local / PoC (Current) | Enterprise Cloud Target (AWS / GCP) |
| :--- | :--- | :--- |
| **Ingestion Source** | `data/raw/*.csv` | Amazon S3 / Google Cloud Storage (`gs://`) |
| **Transform Engine** | Pandas (In-Memory) | AWS Glue, Dataproc, or dbt Core |
| **Target Warehouse** | SQLite (`sales.db`) | PostgreSQL (RDS), Snowflake, BigQuery |
| **Orchestrator** | CLI / Task Scheduler | Apache Airflow (Cloud Composer / AWS MWAA) |
| **Reporting / BI** | Markdown / HTML Reports | Power BI, Looker Studio, Tableau |

### Migration to PostgreSQL Example:
To target PostgreSQL instead of SQLite, simply update the SQLAlchemy connection URL in `src/config.py`:
```python
# SQLite (Local):
db_connection_url = "sqlite:///data/processed/sales.db"

# PostgreSQL (Production):
db_connection_url = "postgresql+psycopg2://user:password@warehouse-host:5432/sales_analytics"
```
No modifications to the transformation, validation, or extraction logic are necessary.
