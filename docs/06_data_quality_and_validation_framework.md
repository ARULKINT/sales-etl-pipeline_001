# 06. Data Quality & Validation Framework

This document outlines the six core data quality dimensions enforced by the pipeline, detailing the rationale behind each transformation and validation rule.

---

## The Six Dimensions of Data Quality

```
      [COMPLETENESS]           [UNIQUENESS]            [VALIDITY]
     Zero missing IDs        No duplicate rows       Positive quantities
     or quantities           or duplicate orders      & formatted dates
           │                       │                       │
           └───────────────────────┼───────────────────────┘
                                   │
                           [DATA INTEGRITY]
                                   │
           ┌───────────────────────┼───────────────────────┐
           │                       │                       │
      [ACCURACY]              [CONSISTENCY]           [TIMELINESS]
   total_price = Qty * Price    Standardized casing    Audit timestamps
   to nearest cent              & ISO date strings     & run latency tracking
```

---

## 1. Cleansing Transformations & Business Rationale

| Transformation Rule | Implementation | Business Rationale |
| :--- | :--- | :--- |
| **Date Normalization** | `pd.to_datetime(..., format="mixed")` | Point-of-sale systems emit dates in locale-specific formats (`YYYY-MM-DD`, `DD/MM/YYYY`, `MM-DD-YYYY`). Normalizing into ISO format enables coherent chronological sorting and partitioning. |
| **Text Normalization** | `.str.strip().str.title()` + Acronym preservation | Eliminates spurious groups like `MOUSE` vs. `Mouse`, while respecting known industry terms (e.g., `USB Cable`). |
| **Missing Value Filtering** | `.dropna(subset=["customer_id", "quantity", ...])` | Transactions missing customer IDs cannot be credited to accounts, loyalty programs, or churn models. Missing quantities cannot be safely estimated without skewing financial records. |
| **Non-Positive Value Removal** | `df[df["quantity"] > 0]` & `df[df["unit_price"] > 0]` | Negative quantities reflect returns, inventory shrinkage, or test events. A clean sales pipeline isolates positive gross transaction revenue. |
| **Deduplication** | `.drop_duplicates(subset=["order_id"])` | Duplicate exports caused by network timeouts or batch retries artificially inflate revenue. Uniqueness of transaction ID is mandatory. |
| **Feature Derivation** | `ROUND(quantity * unit_price, 2)` | Derives canonical transactional spend in the pipeline, removing ambiguity in downstream queries. |

---

## 2. Validation Assertions Gate

Prior to loading into the database, `src/validate.py` executes 8 programmatic assertions. If any assertion fails, a `ValidationError` is raised, halting pipeline execution and preventing dirty data persistence.

```python
def validate_data(df: pd.DataFrame, config: Optional[PipelineConfig] = None) -> Dict[str, bool]:
    # 1. Non-Empty Assertion
    assert len(df) > 0, "DataFrame is empty after transformation"

    # 2. Schema Completeness Assertion
    assert required_cols.issubset(df.columns), f"Missing required columns"

    # 3. Null Absence Assertion
    assert df[required_cols].isnull().sum().sum() == 0, "Unexpected nulls found"

    # 4. Strictly Positive Quantity Assertion
    assert (df["quantity"] >= 1).all(), "Non-positive quantities detected"

    # 5. Strictly Positive Price Assertion
    assert (df["unit_price"] > 0).all(), "Non-positive unit prices detected"

    # 6. Calculation Parity Assertion
    assert np.isclose(df["total_price"], (df["quantity"] * df["unit_price"]).round(2), atol=0.01).all()

    # 7. Uniqueness Assertion
    assert df["order_id"].duplicated().sum() == 0, "Duplicate order_ids detected"

    # 8. Regex Pattern Matching Assertion
    assert df["customer_id"].str.match(r"^CUST\d{3}$").all(), "Invalid customer ID pattern"
```

---

## 3. Data Quality Scorecard (Empirical Benchmark)

Based on the 508-row synthetic messy baseline dataset:

| Quality Indicator | Pre-Cleaning (Raw) | Post-Cleaning (Processed) | Status |
| :--- | :--- | :--- | :--- |
| **Total Record Count** | 508 | 472 | 36 bad rows dropped (92.91% retention) |
| **Missing Customer IDs** | 15 rows | 0 rows | **100% Resolved** |
| **Missing Quantities** | 10 rows | 0 rows | **100% Resolved** |
| **Negative Quantities** | 5 rows | 0 rows | **100% Resolved** |
| **Duplicate Orders** | 8 rows | 0 rows | **100% Resolved** |
| **Unstandardized Product Strings** | 24 variations | 8 canonical names | **100% Standardized** |
| **Mathematical Accuracy** | N/A (uncalculated) | 100% verified (`total_price`) | **100% Verified** |

---

## 4. Production Quarantine & Dead-Letter Architecture

In larger enterprise installations, records that fail validation should not merely be discarded; they should be directed to a **Dead-Letter Queue (DLQ)** or quarantine table:

```
Raw Record ──► Validation Check ──┬──► [Pass] ──► sales Table (Production)
                                  │
                                  └──► [Fail] ──► sales_quarantine Table + Alert
```

The quarantine schema captures:
* Raw record payload as JSON.
* Failure reason / rule violated (e.g., `MISSING_CUSTOMER_ID`).
* Ingestion timestamp and source filename for triage by data stewards.
