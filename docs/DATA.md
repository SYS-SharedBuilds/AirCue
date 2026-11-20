# AirCue Dataset Documentation

## Overview & Provenance
AirCue utilizes ambient air quality and meteorological data to simulate and validate outdoor school alert logic.

- **Primary Provider**: Open-Meteo Air Quality API (`https://air-quality-api.open-meteo.com/v1/air-quality`)
- **Dataset Kind**: `model_cams` (Copernicus Atmosphere Monitoring Service reanalysis/forecast models operated by ECMWF).
- **Attribution**: Contains modified Copernicus Atmosphere Monitoring Service information [2026]. Data provided via Open-Meteo under Non-Commercial / Attribution terms.
- **Important Distinction**: This dataset represents high-resolution atmospheric numerical model output rather than direct physical sensor hardware measurements. Model reanalysis accounts for boundary layer dispersion, meteorological transport, and regional emissions.

## Geographic Selection: 14 Major Cities Across Madhya Pradesh
The dataset focuses on Madhya Pradesh to model air quality across the regional deployment zone:
1. **Indore (Primary Deployment Site)**: 22.7196° N, 75.8577° E (PIEMR campus, Malwa plateau).
2. **Bhopal**: 23.2599° N, 77.4126° E (State capital, lake basin topography).
3. **Jabalpur**: 23.1815° N, 79.9864° E (Mahakoshal regional hub).
4. **Gwalior**: 26.2183° N, 78.1828° E (Northern MP, alluvial basin, higher particulate load).
5. **Ujjain**: 23.1765° N, 75.7885° E (Malwa spiritual and cultural center).
6. **Sagar**: 23.8388° N, 78.7378° E (Bundelkhand central university city).
7. **Ratlam**: 23.3315° N, 75.0367° E (Western commercial and transit junction).
8. **Dewas**: 22.9676° N, 76.0534° E (Industrial belt adjacent to Indore).
9. **Satna**: 24.6005° N, 80.8322° E (Cement and limestone industrial center).
10. **Rewa**: 24.5362° N, 81.3037° E (Vindhya regional hub).
11. **Singrauli**: 24.1997° N, 82.6645° E (Energy hub, coal mining and thermal power pollution regime).
12. **Katni**: 23.8343° N, 80.3957° E (Mineral processing and railway nexus).
13. **Burhanpur**: 21.3109° N, 76.2299° E (Southern MP, Nimar region on Tapti river).
14. **Morena**: 26.4947° N, 77.9940° E (Chambal division, northern plains).

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
