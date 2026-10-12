# 10. Contributing & Developer Guide

Welcome to the Sales ETL Pipeline developer documentation. This guide details development workflows, contribution standards, and extensibility patterns.

---

## 1. Development Workflow

### Git Branching Conventions
* `main`: Production-ready, stable codebase.
* `feature/<feature-name>`: New transformation logic, source adapters, or reporting capabilities.
* `bugfix/<issue-name>`: Corrections for data parsing edge cases or validation assertion updates.

```bash
git checkout -b feature/add-customer-loyalty-tiers
```

---

## 2. Code Quality & Standards

* **PEP 8 Compliance:** All Python code adheres to PEP 8 standards (4-space indentation, descriptive identifiers).
* **Type Hinting:** Mandatory type hints on all public function signatures.
* **Docstrings:** Use Google-style or standard Sphinx docstrings specifying parameters, return types, and exceptions raised.
* **Cross-Platform Safety:** Never use non-ASCII emoji characters in console print statements or unencoded file handlers that may break on Windows `cp1252` terminals.

---

## 3. How-To: Add a New Transformation Rule

To add a new cleaning or feature engineering step:

1. Open `src/transform.py`.
2. Define your function taking and returning a `pd.DataFrame`:
   ```python
   def add_loyalty_tier(df: pd.DataFrame) -> pd.DataFrame:
       """Categorizes customers into Gold, Silver, or Bronze tiers based on total spend."""
       df = df.copy()
       df["loyalty_tier"] = pd.cut(
           df["total_price"],
           bins=[0, 100, 500, float("inf")],
           labels=["Bronze", "Silver", "Gold"]
       )
       return df
   ```
3. Register the function inside `transform_pipeline()`:
   ```python
   def transform_pipeline(df: pd.DataFrame, config: Optional[PipelineConfig] = None) -> pd.DataFrame:
       ...
       df = add_calculated_columns(df)
       df = add_loyalty_tier(df)  # <-- Added step
       return df.reset_index(drop=True)
   ```
4. If your new column is mandatory for analytics, add it to `required_clean_columns` in `src/config.py`.
5. Add a unit test in `tests/test_transform.py`.
6. Run `pytest tests/` to verify.

---

## 4. How-To: Add a New Analytical SQL Query

1. Open `sql/queries.sql`.
2. Append your query with a descriptive comment header:
   ```sql
   -- Query 7: High-value transaction distribution
   SELECT
       loyalty_tier,
       COUNT(*) AS transaction_count,
       ROUND(SUM(total_price), 2) AS tier_revenue
   FROM sales
   GROUP BY loyalty_tier
   ORDER BY tier_revenue DESC;
   ```
3. The query is automatically parsed, executed, exported to CSV, and embedded into the Executive Report on the next pipeline execution.

---

## 5. Pre-Commit Checklist

Before pushing commits:
1. Run `pytest tests/ -v` (Must achieve 100% pass rate).
2. Execute `python src/main.py` and inspect `reports/pipeline_execution_report.md`.
3. Check `git status` to ensure temporary test artifacts are excluded.
