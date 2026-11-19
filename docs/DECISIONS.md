# AirCue Architectural Decision Records (ADRs)

## ADR-001: Outdoor Air Quality Domain Stance (CO2 vs Particulate AQI)
- **Status:** Accepted
- **Context:** The reference guide `Classroom_Voice_Feedback_System_Speaks_When_CO2_Rises.pdf` was developed for indoor classroom ventilation where CO2 accumulation (800–2000 ppm) indicates insufficient fresh air exchange, prompting advice such as "open the window/door". In outdoor school settings (assembly areas, sports fields, playgrounds, entrance/dismissal areas), ambient CO2 remains baseline (~420 ppm) and conveys zero actionable safety information. Outdoor environmental hazards in Indian cities predominantly comprise particulate matter (PM2.5, PM10).
- **Decision:** AirCue uses ambient PM2.5 and PM10 as the primary sensor inputs, evaluated against the India Central Pollution Control Board (CPCB) National Air Quality Index (NAQI). Indoor ventilation advice (opening doors/windows, stuffiness) is strictly forbidden. Spoken guidance targets outdoor activity regulation (limiting vigorous exercise, shifting activities indoors, cancelling outdoor sports).
- **Consequences:** The trigger state machine, message templates, hardware enclosures, and audio acoustic parameters are entirely re-architected for outdoor environmental deployment.

## ADR-002: Verification and Citation Integrity Policy
- **Status:** Accepted
- **Context:** Academic rigor prohibits fabricated or unverified citations in scientific publications.
- **Decision:** Every academic citation in `paper/refs.bib` must trace directly to official standards (e.g. CPCB NAQI guidelines, WHO Air Quality Guidelines) or peer-reviewed literature. Any entry not verified offline against primary databases is flagged with `% VERIFY: <reason>` in `paper/refs.bib` and catalogued in this document.
- **Pending Citations To Verify:**
  1. `CPCB2014NAQI`: Central Pollution Control Board, "National Air Quality Index", Ministry of Environment, Forest and Climate Change, 2014. [Verify exact publication title and report number]
  2. `WHO2021AQG`: World Health Organization, "WHO global air quality guidelines: particulate matter (PM2.5 and PM10), ozone, nitrogen dioxide, sulfur dioxide and carbon monoxide", 2021.
  3. `Kumar2021LowCostSensors`: Low-cost sensor evaluation and calibration in Indian urban ambient environments. [Verify exact authors, journal, DOI]

## ADR-003: Model Selection & Discovery Filter Rules
- **Status:** Accepted
- **Context:** Free-tier model availability on OpenRouter shifts rapidly. Sorting by context length biases selection towards 1M-context experimental/preview models, while pulling in sub-7B models (such as 1.7B parameter models) leads to high failure rates on Hindi and structured JSON tasks, skewing system evaluation.
- **Decision:** Model discovery applies deterministic filtering:
  1. Parameter size check: reject models smaller than 7B parameters.
  2. Slug filter: drop identifiers containing `-preview`, `preview`, `-music`, `-audio`, `-vl`, `-code`, `-exp`, or `promo`.
  3. Family priority: Check preferred families `[deepseek, moonshotai]`. If free models exist, include them. If none exist, log notice and prioritize established open-weight families (Google Gemma, NVIDIA Nemotron).
  4. Quota and cost control: `allow_paid_preferred` toggle (default `false`). When enabled with an OpenRouter top-up, resolves the cheapest paid DeepSeek and Moonshot/Kimi models.
  5. Deterministic sorting: sort valid candidates by family priority, then alphabetically by model ID.

## ADR-004: India CPCB National AQI Breakpoint Tables
- **Status:** Accepted
- **Context:** CPCB calculates sub-indices for PM2.5 and PM10 using linear interpolation across designated breakpoint ranges.
- **Breakpoints (µg/m³):**
  - **PM2.5 (24-hr average standard, applied hourly for real-time alerts):**
    - Good (0–50): 0–30
    - Satisfactory (51–100): 31–60
    - Moderate (101–200): 61–90
    - Poor (201–300): 91–120
    - Very Poor (301–400): 121–250
    - Severe (401–500): >250
  - **PM10:**
    - Good (0–50): 0–50
    - Satisfactory (51–100): 51–100
    - Moderate (101–200): 101–250
    - Poor (201–300): 251–350
    - Very Poor (301–400): 351–430
    - Severe (401–500): >430
- **Alert Cadence vs 24-hr Window:** Official CPCB AQI is reported over a 24-hour rolling window. AirCue uses 1-hour average / hourly values for immediate actionable alert dispatch, while documenting the distinction clearly.

## ADR-005: Empirical Optical PM Humidity Correction
- **Status:** Accepted
- **Context:** Light-scattering optical particle counters (e.g. PMS5003, SPS30) overestimate particulate mass when relative humidity exceeds 70% due to hygroscopic water absorption on aerosol surfaces.
- **Decision:** Provide an optional empirical correction factor based on $\kappa$-Köhler hygroscopic growth: $PM_{corr} = PM / (1 + a \cdot (RH / (100 - RH))^b)$ with configurable parameters (default disabled, recommend co-location calibration).
