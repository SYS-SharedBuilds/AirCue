# AirCue: Outdoor Air-Quality Voice Announcer & LLM Benchmark System

AirCue is an event-driven **outdoor air-quality voice alert system for schools** (assembly areas, sports fields, playgrounds, entrance/dismissal areas). It continuously monitors ambient particulate matter (PM2.5, PM10) and India CPCB National AQI, autonomously speaking over public address systems when conditions deteriorate or recover.

AirCue is strictly for **outdoor environmental monitoring**. It does NOT monitor indoor ventilation or CO2, and never dispenses indoor advice (such as opening windows/doors).

---

## 5-Minute Quickstart

```bash
# 1. Create and activate environment
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -e ".[dev,tts]"

# 3. Fetch real AQI dataset snapshot from Open-Meteo API
aircue data fetch

# 4. Run an offline mock benchmark demonstration
aircue benchmark run --mock --limit 10

# 5. Build pregenerated audio clips
aircue clips build --backend beep
```

For full setup, live OpenRouter evaluation, ESP32 firmware flashing, and paper generation, see `docs/RUNBOOK.md`.
