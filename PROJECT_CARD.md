# Project Card - Phase 1

## Identity and decision context
- **Track / subset:** NYC TLC Yellow Taxi Trip Records; January 2024 monthly Parquet (2,964,624 rows).
- **Working title:** Hour-ahead Yellow Taxi pickup-demand forecasting by TLC zone.
- **Decision supported:** deploy vehicles and driver incentives before a zone-hour begins.
- **Unit of source observation / prediction:** one provider-submitted trip row / one TLC zone-hour. Future modeling must create a complete zone-hour grid including zero-pickup cells.
- **Target population:** Yellow Taxi trips reported to NYC TLC. This is operational reporting data, not a random sample of all NYC trips.

## Questions
1. How do pickup volumes vary by hour, weekday, and pickup zone?
2. Does a zone's recent pickup history improve hour-ahead demand forecasts over seasonal-naive forecasts?
3. Which zone-hour periods show unusual volume relative to their historical hour-of-week level?

**Selected question:** Q2. Predict next-hour pickup count for a zone using only information available strictly before that hour.

## Target, baseline, metrics, split
- **Target:** number of provider-submitted pickups in zone `z` during future interval `[t+1,t+2)`, where `t` is the latest completed hour.
- **Baseline:** seasonal-naive count for the same zone and hour-of-week from prior weeks (fallback: zone historical mean).
- **Metrics:** MAE and RMSLE on counts; report total-volume bias by borough/zone where lookup data are added.
- **Split:** proposed chronological train Jan-Oct 2024, validation Nov 2024, test Dec 2024; fit feature transforms on train only. This cannot be executed with the January-only audit file.

## Leakage and integrity risks
- Do not use dropoff time, dropoff zone, fare/tip/total, or any record field realized after pickup to predict future demand.
- Random row splits leak temporally adjacent and same-hour demand patterns; split by time.
- Duplicate-looking trips are not automatically duplicates: many genuine trips share a time/zone. Exact full-row duplicates are audited, and no records are removed from demand counts on that basis.
- Vendor reporting delays and late corrections can make near-real-time availability differ from the published file.

## Unsupervised / advanced component
Cluster standardized zone-level hourly profiles (hour-of-week proportions, typical distance, payment mix) and inspect anomalies as deviations from cluster/seasonal profiles. Time-series/event analysis is the relevant advanced component.

## Ethics, privacy, governance
TLC says it does not collect passenger information, but precise time/zone trajectories can still expose sensitive mobility patterns at small aggregation levels. Publish only aggregate zone-hour results, avoid re-identification attempts, document reporting biases and vendor data limitations, and do not infer causal impacts from observational patterns.
