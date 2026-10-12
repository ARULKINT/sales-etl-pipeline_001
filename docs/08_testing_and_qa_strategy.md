# 08. Testing & Quality Assurance (QA) Strategy

This document details the comprehensive testing framework implemented for the Sales ETL Pipeline.

---

## Testing Philosophy & Pyramid

```
                ┌──────────────────────┐
                │     E2E Pipeline     │  (1 Integration Scenario)
                │     End-to-End       │  Complete file-to-report flow
                └──────────┬───────────┘
                           │
                ┌──────────┴───────────┐
                │   Component Tests    │  (Load, Analytics, Profile)
                │   Cross-Module       │  DB transactions, Query engine
                └──────────┬───────────┘
                           │
          ┌────────────────┴────────────────┐
          │        Unit Test Foundation     │  (24 Unit Tests)
          │  Extract, Transform, Validate   │  Isolated deterministic assertions
          └─────────────────────────────────┘
```

---

## Test Suite Inventory (30 Automated Tests)

| Test File | Target Module | Test Count | Key Scenarios Covered |
| :--- | :--- | :--- | :--- |
| `tests/test_extract.py` | `src/extract.py` | 5 | Valid CSV read, `FileNotFoundError` handling, empty CSV rejection, missing required headers detection, multi-file glob extraction. |
| `tests/test_profile.py` | `src/profile_data.py` | 3 | Profiling metric dictionary keys, before/after `compare_profiles` calculations, console output formatting. |
| `tests/test_transform.py` | `src/transform.py` | 8 | Mixed date format parsing, text casing and acronym preservation, missing value dropping, invalid row removal, data type casting (`int64`/`float64`), calculated column generation, deduplication, and complete transformation pipeline execution. |
| `tests/test_validate.py` | `src/validate.py` | 8 | Passing valid dataset, rejection of empty DataFrame, rejection of missing schema columns, rejection of unexpected nulls, non-positive quantity detection, mathematical calculation mismatch detection, duplicate order ID detection, invalid customer regex pattern detection. |
| `tests/test_load.py` | `src/load.py` | 2 | SQLite database table replacement and row count verification, audit table (`etl_pipeline_audit`) row generation and field verification. |
| `tests/test_analytics.py` | `src/analytics.py` | 3 | SQL query file comment parsing, multi-query execution and KPI computation, CSV analytics export generation. |
| `tests/test_pipeline_e2e.py` | `src/main.py` | 1 | Complete end-to-end integration test from synthetic messy CSV ingestion through SQLite persistence, KPI computation, and Markdown/HTML report generation. |

---

## Running the Test Suite

### 1. Run All Tests
```bash
pytest tests/ -v
```

### 2. Run Specific Module Test
```bash
pytest tests/test_transform.py -v
```

### 3. Run Specific Test Case by Name
```bash
pytest -k "test_clean_dates" -v
```

### 4. Run with Code Coverage (Optional)
If `pytest-cov` is installed:
```bash
pytest --cov=src --cov-report=term-missing tests/
```

---

## Test Isolation & Fixture Design

Tests use `pytest`'s built-in `tmp_path` fixture to create isolated filesystem workspaces. No test modifies production files or the primary `data/processed/sales.db` database.

Example fixture pattern:
```python
@pytest.fixture
def temp_db(tmp_path):
    """Creates a temporary isolated SQLite database file."""
    db_file = tmp_path / "test_sales.db"
    cfg = PipelineConfig(processed_db_path=db_file)
    return {"cfg": cfg, "path": db_file}
```
All artifacts created during testing are automatically garbage-collected by the operating system after the test session concludes.
