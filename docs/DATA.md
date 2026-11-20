# AirCue Dataset Documentation

## Overview & Provenance
AirCue utilizes ambient air quality and meteorological data to simulate and validate outdoor school alert logic.

- **Dual-Tier Data Architecture**:
  1. **Physical Ground-Station Measurements (`measured_station`)**: Real physical sensor observations from Continuous Ambient Air Quality Monitoring Stations (CAAQMS) operated by MPPCB (Madhya Pradesh Pollution Control Board), CPCB, IMC, and industrial partners across specific urban localities in MP. Ingested via OpenAQ v3 API with verified physical sensor identifiers.
  2. **Atmospheric Gridded Reanalysis (`model_cams`)**: Statewide continuous baseline from the Copernicus Atmosphere Monitoring Service (CAMS) operated by ECMWF, retrieved via Open-Meteo.
- **Attribution**: Ground station physical telemetry courtesy of CPCB/MPPCB/OpenAQ. Numerical model data contains modified Copernicus Atmosphere Monitoring Service information [2026] via Open-Meteo.
- **Important Distinction**: AirCue strictly differentiates between physical station measurements (`dataset_kind = "measured_station"`) and gridded numerical models (`dataset_kind = "model_cams"`). Ground stations capture intra-city hyper-local particulate variations (e.g., traffic hotspots vs. regional parks).

## Physical Monitoring Stations & Urban Localities (OpenAQ v3 / CPCB / MPPCB)
AirCue actively monitors 32 physical ground monitoring stations capturing distinct locality-level air quality within Madhya Pradesh cities:

- **Indore Localities (6 stations)**:
  - `Vijay Nagar Scheme-78, Indore - Glenmark` (Commercial / residential hub)
  - `Chhoti Gwaltoli, Indore - MPPCB` (High-density transit / railway station corridor)
  - `Residency Area, Indore - IMC` (Administrative green belt)
  - `Regional Park, Indore - MPPCB` (Urban green zone / lake boundary)
  - `Maguda Nagar, Indore - IMC` (Dense mixed residential area)
  - `Airport Area, Indore - IMC` (Western periphery / aviation corridor)
- **Bhopal Localities (4 stations)**:
  - `T T Nagar, Bhopal - MPPCB`
  - `Paryavaran Parisar, Bhopal - MPPCB`
  - `Idgah Hills, Bhopal - MPPCB`
  - `Industrial Area, Govindpura, Bhopal`
- **Jabalpur Localities (4 stations)**:
  - `Marhatal, Jabalpur - MPPCB`
  - `Suhagi, Jabalpur - JMC`
  - `Gupteshwar, Jabalpur - JMC`
  - `Govindh Bhavan Colony, Jabalpur - MPPCB`
- **Gwalior Localities (4 stations)**:
  - `City Center, Gwalior - MPPCB`
  - `Maharaj Bada, Gwalior - MPPCB`
  - `Deen Dayal Nagar, Gwalior - MPPCB`
  - `Phool Bagh, Gwalior - Mondelez Ind. Food`
- **Ujjain Localities (2 stations)**:
  - `Mahakaleshwar Temple, Ujjain - MPPCB`
  - `Mahashweta Nagar, Ujjain - MPPCB`
- **Sagar Localities (2 stations)**:
  - `Civil Lines, Sagar - MPPCB`
  - `Deen Dayal Nagar, Sagar - MPPCB`
- **Industrial & Regional Localities**:
  - `Sector-2 Industrial Area, Pithampur - MPPCB` (Major auto hub near Indore)
  - `Sector-D Industrial Area, Mandideep - MPPCB` (Industrial hub near Bhopal)
  - `Bhopal Chauraha, Dewas - MPPCB`
  - `Shasthri Nagar, Ratlam - IPCA Lab`
  - `Gole Bazar, Katni - MPPCB`
  - `Birla Staff colony, Satna - MPPCB`
  - `Bandhavgar Colony, Satna - Birla Cement`
  - `Vindhyachal STPS, Singrauli - MPPCB` (Thermal power generation cluster)
  - `Shrivastav Colony, Damoh - MPPCB`
  - `Sahilara, Maihar - KJS Cements`

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
