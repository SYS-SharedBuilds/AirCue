# AirCue Dataset Documentation

## Overview & Provenance
AirCue utilizes ambient air quality and meteorological data to simulate and validate outdoor school alert logic.

- **Primary Provider**: Open-Meteo Air Quality API (`https://air-quality-api.open-meteo.com/v1/air-quality`)
- **Dataset Kind**: `model_cams` (Copernicus Atmosphere Monitoring Service reanalysis/forecast models operated by ECMWF).
- **Attribution**: Contains modified Copernicus Atmosphere Monitoring Service information [2026]. Data provided via Open-Meteo under Non-Commercial / Attribution terms.
- **Important Distinction**: This dataset represents high-resolution atmospheric numerical model output rather than direct physical sensor hardware measurements. Model reanalysis accounts for boundary layer dispersion, meteorological transport, and regional emissions.

## Multi-City Geographic Selection
The dataset incorporates 6 diverse Indian urban environments spanning distinct pollution regimes:
1. **Indore (Primary Deployment Site)**: 22.7196° N, 75.8577° E (PIEMR campus, central plateau).
2. **Bhopal**: 23.2599° N, 77.4126° E (Central lake basin).
3. **Delhi (NCR)**: 28.6139° N, 77.2090° E (High particulate regime; critical representation of Very Poor and Severe levels).
4. **Mumbai**: 19.0760° N, 72.8777° E (Coastal regime, high relative humidity).
5. **Kolkata**: 22.5726° N, 88.3639° E (Eastern river delta, seasonal winter inversions).
6. **Bengaluru**: 12.9716° N, 77.5946° E (Southern elevation plateau, predominantly Good to Moderate).

## Schema
Tidy CSV structure (`data/snapshots/aqi_snapshot_<date>.csv`):
- `timestamp`: ISO-8601 string with Asia/Kolkata timezone (`+05:30`).
- `location`: City name.
- `lat`, `lon`: Geographic coordinates.
- `pm2_5`: Particulate matter ≤ 2.5 µm concentration (µg/m³).
- `pm10`: Particulate matter ≤ 10 µm concentration (µg/m³).
- `us_aqi`: Calculated US EPA Air Quality Index.
- `european_aqi`: European Air Quality Index.
- `ozone`, `no2`, `so2`, `co`: Trace gas concentrations.
- `cpcb_aqi`: Calculated India CPCB National AQI from PM sub-indices.
- `cpcb_category`: CPCB category (`Good`, `Satisfactory`, `Moderate`, `Poor`, `Very Poor`, `Severe`).
- `provider`: `open_meteo`.
- `dataset_kind`: `model_cams`.
- `fetched_at`: Ingestion timestamp.

## Incremental Maintenance Cron
Because Open-Meteo provides a 92-day rolling historical window, deploy the cron job `deploy/cron.example` to run `aircue data update` daily to expand the permanent local dataset archive without gaps.
