# Data Analysis Project - Phase 1

This repository audits January 2024 NYC TLC Yellow Taxi trip records and defines an hour-ahead zone-demand forecasting project.

## Reproduce

Run the following commands from the project root. The recorded analysis environment is listed in `outputs/package_versions.txt` (Python 3.12.14).

```bash
python -m pip install -r requirements.txt
python scripts/acquire_data.py
python scripts/phase1_eda.py --input data/yellow_tripdata_2024-01.parquet
python scripts/build_phase1_report.py
```

The acquisition file is official TLC monthly Parquet data (49,961,641 bytes) and is excluded from the ZIP. Seed `20261108` selects a 50,000-row diagnostic trip-variable sample. Quality rules use raw rows; demand counts intentionally use January pickups with PULocationID 1-263 and do not filter on fares, duration or speed. Codes 264 (Unknown/N/A) and 265 (Outside of NYC) are recognized special TLC codes, outside this chosen study population rather than automatically corrupt. Join a TLC zone lookup by `PULocationID` or `DOLocationID` to its `LocationID`; the 1-263 range includes Newark Airport. Dropoff counts use all January pickup records with DOLocationID 1-263, regardless of pickup-zone validity. Calculated speed is defined only for finite, nonnegative distance and finite, strictly positive duration; the numeric speed summary reports its valid denominator. Capture the execution log with `python scripts/phase1_eda.py --input data/yellow_tripdata_2024-01.parquet > outputs/run_log.txt 2>&1`.

To rebuild only the PDF from the supplied validated outputs and figures, run `python scripts/build_phase1_report.py`. This does not download data or rerun the EDA.

## Outputs

- `reports/phase1.pdf`: rendered Phase 1 report.
- `outputs/audit_summary.json`, CSV tables, and `figures/`: generated evidence.
- `PROJECT_CARD.md`: project registration details.
- `AI_USAGE.md`: transparent tool-use record.
- `PHASE1_EXECUTION_CHECKLIST.md`: requirement-level evidence and remaining verification limits.

## Sources and licensing/access notes

- TLC Trip Record Data: <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>
- TLC Yellow Taxi Data Dictionary: <https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf>
- The TLC page states records are submitted by authorized technology providers and TLC does not guarantee accuracy/completeness. Use is subject to the source's terms; no claim of a separate open-data license is made here.

## Scope limitation

This Phase 1 uses only January 2024. The proposed Jan-Oct/Nov/Dec temporal split cannot be run yet. No model was trained.
