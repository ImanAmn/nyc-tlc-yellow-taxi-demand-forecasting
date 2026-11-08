# Data acquisition

Selected file: `yellow_tripdata_2024-01.parquet`.

- URL: `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.parquet`
- Publisher: NYC Taxi & Limousine Commission (TLC)
- Downloaded for this audit: 2026-11-08
- File size observed: 49,961,641 bytes
- Format: Apache Parquet
- Unit: one submitted Yellow Taxi trip record

Run `python scripts/acquire_data.py` to reproduce acquisition. Do not commit the Parquet data file.

## Candidate comparison (inspection only; no large downloads)

| Candidate | Official access / format | Scale / key constraint | Phase-1 feasibility |
|---|---|---|---|
| NYC TLC (chosen) | TLC monthly Parquet + data dictionary | Jan-2024 file 49.96 MB; tabular trips, time and zones | High: bounded official sample, explicit audit requirements |
| Amazon Reviews'23 (backup) | Project site / category review and metadata downloads | 571.54M reviews overall; text, metadata, user-item links; missing modalities/identity split must be handled | Medium: use a small declared category only |
| iNaturalist Open Data | AWS Registry S3, JPEG + monthly metadata | image license varies CC/CC0; image/observation/taxon joins and long-tail labels | Low-medium under deadline |
| Speech Commands v0.02 | TensorFlow Datasets | 2.37 GiB download, 8.17 GiB prepared; audio/speaker-disjoint analysis | Medium but heavier compute/audio workflow |

Selection rationale: NYC TLC has the smallest directly auditable official monthly artifact, a transparent tabular schema, controlled compute cost, and natural support for time-series, clustering, regression/classification, and robust chronological evaluation across all five phases. Backup is Amazon Reviews'23, restricted to a documented small category such as All_Beauty; it adds text and multimodal complexity but remains feasible if an approved small slice is acquired.

Sources: TLC <https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page>; Amazon Reviews'23 <https://amazon-reviews-2023.github.io/>; iNaturalist AWS Registry <https://registry.opendata.aws/inaturalist-open-data/>; TensorFlow Datasets Speech Commands <https://www.tensorflow.org/datasets/catalog/speech_commands>.
