# AirCue Architecture Documentation

## 1. Domain Stance: Outdoor Air Quality vs Indoor Ventilation
The reference design (`Classroom_Voice_Feedback_System_Speaks_When_CO2_Rises.pdf`) governed indoor classroom spaces where metabolic carbon dioxide ($CO_2$) builds up from student respiration, prompting instructions like *"The air is stuffy; kindly open the windows and doors."*

**AirCue is explicitly deployed outdoors** (morning assembly quadrangle, sports fields, playgrounds, entrance/dismissal bus gates). In outdoor urban India:
1. **$CO_2$ is ambient (~420 ppm)** and conveys zero actionable risk.
2. **Particulate Matter (PM2.5 and PM10)** constitutes the primary health hazard.
3. Indoor advice (opening doors or windows) is strictly forbidden. Guidance regulates physical exercise intensity and outdoor-to-indoor transitions.

---

## 2. Component Pipeline Architecture

```
[Outdoor ESP32 Node (PMS5003 + BME280)]
                 │
                 ▼ (MQTT Telemetry)
┌────────────────────────────────────────────────────────┐
│               Raspberry Pi Service                     │
│                                                        │
│  1. Ingestion & Empirical Humidity Correction          │
│     - PM_corr = PM / (1 + factor * (RH / (100 - RH))) │
│                                                        │
│  2. CPCB Sub-Index & AQI Calculation                   │
│     - Linear interpolation across official breakpoints │
│                                                        │
│  3. Deterministic State Machine (AQIMonitor)           │
│     - Sustained confirmation (T_confirm = 3600s)       │
│     - Multi-level hysteresis & reminder cadence       │
│                                                        │
│  4. Operational Gating                                 │
│     - Schedule: School hours & timetable slot         │
│     - Controls: Mute, 30-min snooze, exam mode        │
│                                                        │
│  5. Message Assembly                                   │
│     - Pre-rendered templates (en, hi)                 │
│     - Optional validated LLM wording cache            │
│                                                        │
│  6. Audio Output                                       │
│     - Non-blocking queued audio player                │
└────────────────────────────────────────────────────────┘
                 │
                 ▼
[High-Gain 30W-50W Amplifier -> Weatherproof Outdoor PA Horn]
```

---

## 3. Reliability & Safety Guarantees
- **Deterministic Trigger Decision**: The decision *when* to speak is executed exclusively in deterministic, side-effect-free Python code (`aircue.trigger.engine`). An LLM is never in the critical path for the decision to speak.
- **Fail-Safe Template Fallback**: Voice clips are pre-rendered into `clips/`. If the LLM is offline, slow, or violates validation rules, audio playback proceeds with guaranteed zero network latency.
- **Zero Audio Input**: The system incorporates no microphone or voice capture capability, ensuring student privacy.
