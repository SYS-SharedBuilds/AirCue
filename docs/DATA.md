# AirCue Dataset Documentation

## Overview & Provenance
AirCue utilizes ambient air quality and meteorological data to simulate and validate outdoor school alert logic.

- **Primary Provider**: Open-Meteo Air Quality API (`https://air-quality-api.open-meteo.com/v1/air-quality`)
- **Dataset Kind**: `model_cams` (Copernicus Atmosphere Monitoring Service reanalysis/forecast models operated by ECMWF).
- **Attribution**: Contains modified Copernicus Atmosphere Monitoring Service information [2026]. Data provided via Open-Meteo under Non-Commercial / Attribution terms.
- **Important Distinction**: This dataset represents high-resolution atmospheric numerical model output rather than direct physical sensor hardware measurements. Model reanalysis accounts for boundary layer dispersion, meteorological transport, and regional emissions.

## Geographic Scope: Full Statewide Coverage (All 55 Districts Across 10 Divisions of Madhya Pradesh)
AirCue incorporates all 55 districts of Madhya Pradesh organized across the 10 administrative divisions:

1. **Indore Division (8 districts)**: Indore (Primary, PIEMR Campus), Dhar, Jhabua, Alirajpur, Khargone (West Nimar), Barwani, Khandwa (East Nimar), Burhanpur.
2. **Ujjain Division (7 districts)**: Ujjain, Dewas, Shajapur, Agar Malwa, Ratlam, Mandsaur, Neemuch.
3. **Bhopal Division (5 districts)**: Bhopal (State Capital), Sehore, Raisen, Rajgarh, Vidisha.
4. **Gwalior Division (5 districts)**: Gwalior, Shivpuri, Guna, Ashoknagar, Datia.
5. **Chambal Division (3 districts)**: Morena, Bhind, Sheopur.
6. **Jabalpur Division (9 districts)**: Jabalpur, Katni, Narsinghpur, Seoni, Chhindwara, Pandhurna, Mandla, Dindori, Balaghat.
7. **Narmadapuram Division (3 districts)**: Narmadapuram, Harda, Betul.
8. **Sagar Division (6 districts)**: Sagar, Damoh, Panna, Chhatarpur, Tikamgarh, Niwari.
9. **Rewa Division (6 districts)**: Rewa, Satna, Sidhi, Singrauli, Mauganj, Maihar.
10. **Shahdol Division (3 districts)**: Shahdol, Anuppur, Umaria.

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
