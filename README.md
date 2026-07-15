# Sales Data ETL Pipeline

A beginner-to-intermediate ETL pipeline that extracts messy raw sales data,
cleans and transforms it, loads it into a SQL database, and runs business
analysis queries against it.

## Problem
Raw sales exports are unreliable — mixed date formats, missing customer IDs,
duplicate rows, invalid quantities. This pipeline turns that mess into
clean, trustworthy data that can answer real business questions like
"what are our top-selling products?"

## Architecture
```
CSV (raw) -> Extract -> Profile -> Transform -> Validate -> Load (SQLite) -> SQL Analysis -> Dashboard
```

## Project Structure
```
sales-etl-pipeline/
├── data/
│   ├── raw/            # raw input CSVs
│   └── processed/      # SQLite database output
├── src/
│   ├── extract.py       # Phase 6
│   ├── profile_data.py  # Phase 7
│   ├── transform.py     # Phase 8
│   ├── validate.py      # Phase 9
│   ├── load.py          # Phase 10
│   └── main.py          # Phase 13 - runs everything
├── sql/
│   └── queries.sql      # Phase 11 - business analysis
├── tests/
│   └── test_transform.py # Phase 14
├── requirements.txt
└── README.md
```

## Setup
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run the pipeline
```bash
python src/main.py
```
This extracts, profiles, cleans, validates, and loads the data — all in
one command, with logging to `pipeline.log`.

## Run tests
```bash
pytest tests/ -v
```

## Run analysis queries
Open `data/processed/sales.db` in DB Browser for SQLite, or run
`sql/queries.sql` against it, to see top products, monthly trends,
top customers, and revenue by region.

## What I learned
- Building a full ETL pipeline from raw data to analysis-ready database
- Writing data validation checks that stop bad data before it's loaded
- Structuring a Python project the way real data engineering teams do
- Testing data transformation logic with pytest
