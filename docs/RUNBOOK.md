# AirCue System Runbook

This runbook documents the exact, reproducible commands to install, test, benchmark, and deploy AirCue.

---

## 1. Environment Installation

```bash
# Clone and enter repo
cd AirCue

# Create and activate Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install package with all developer, TTS, and dashboard extras
pip install --upgrade pip
pip install -e ".[dev,tts,dashboard]"
```

---

## 2. Air Quality Dataset Workflow

### A. Fetch 92-Day Real Multi-City Data (Keyless Open-Meteo)
```bash
aircue data fetch
```
*Expected Output*: Fetches 92 days of hourly particulate data across 6 cities (Indore, Bhopal, Delhi, Mumbai, Kolkata, Bengaluru) and commits `data/snapshots/aqi_snapshot_<date>.csv` with a cryptographic SHA-256 JSON manifest.

### B. Inspect Dataset EDA Statistics
```bash
aircue data inspect
```
*Expected Output*: Prints tabular rows, PM2.5 mean/std, CPCB AQI distribution, and missing value rates.

### C. Daily Incremental Sync & Cron Setup
```bash
# Incremental update command (appends recent data & dedupes on location+timestamp+provider)
aircue data update

# To automate daily sync at 01:00 AM IST, install cron job:
crontab deploy/cron.example
```

---

## 3. Trigger State Machine Replay & Tuning

```bash
# Run deterministic state machine replay over dataset snapshot
aircue replay --location Indore

# Parameter grid sweep (confirmation delay vs announcements per day)
aircue tune --location Indore
```
*Generated Artifact*: AQI timeline plot saved to `results/replay/aqi_timeline_indore.png`.

---

## 4. Audio Clip Pregeneration

```bash
# Pregenerate all 200 template clips in English and Hindi (offline beep synthesizer for testing)
aircue clips build --backend beep

# Pregenerate with gTTS (internet required) or piper-tts
aircue clips build --backend gtts --force
```
*Generated Artifact*: Pre-rendered WAV files and `clips/manifest.json`.

---

## 5. LLM Benchmarking Pipeline

### A. Discover Free Models & Snapshot
```bash
aircue models discover
```
*Note*: Automatically applies ADR-003 filters (drops sub-7B parameter models, preview/promo/multimodal slugs) and prioritizes Google Gemma and NVIDIA Nemotron. Saves `results/models/discovered_<date>.json`.

### B. Plan Benchmark Run & Days Calculation
```bash
aircue benchmark plan
```
*Expected Output*: Prints total calls (e.g. 1,040 calls), calls per model, and projected run duration under daily budget (e.g. 6 days under 180 req/day free budget).

### C. Run Benchmark (Offline Mock Mode)
```bash
aircue benchmark run --mock --limit 10
```

### D. Run Benchmark (Live with OpenRouter Key)
1. Add key to `.env`:
   ```bash
   echo "OPENROUTER_API_KEY=your_key_here" >> .env
   ```
2. Run benchmark:
   ```bash
   aircue benchmark run
   ```
*Resume Support*: The runner automatically logs progress to `results/raw/latest_run.jsonl`. When the daily 180-request quota is hit, it halts cleanly. Simply re-run on subsequent days to resume without duplicate calls.

### E. Compile Reports & LaTeX Tables
```bash
aircue benchmark report
```
*Generated Artifacts*:
- `results/report/summary.md`
- `paper/tables/benchmark_summary.tex`
- `paper/figures/model_pass_rates.png` / `.pdf`

---

## 6. Research Paper Compilation

```bash
# Ingest latest benchmark metrics into LaTeX macros
python3 paper/build_results.py

# Compile IEEE conference paper
make -C paper
```

---

## 7. Interactive Streamlit Dashboard

```bash
streamlit run src/aircue/dashboard/app.py
```
Provides visual exploration of particulate timelines, CPCB category bands, and live playback of synthesized audio clips.

---

## 8. Simulated Node & Raspberry Pi Service Deployment

```bash
# Test simulated outdoor node publishing telemetry over MQTT:
aircue sim-node --site indore_school_01 --count 5

# Run main audio alert service listening to replay/virtual sensor:
aircue run --source replay --location Indore --speed 10.0

# Deploy on Raspberry Pi:
bash deploy/install_pi.sh
```

---

## 9. Future: Enabling Claude Models (Zero Code Changes)
To evaluate Anthropic Claude models once an API key is available:
1. Put `ANTHROPIC_API_KEY=your_key` in `.env`.
2. In `configs/benchmark.yaml`, toggle `anthropic.enabled: true`.
3. Re-run `aircue benchmark run`.
