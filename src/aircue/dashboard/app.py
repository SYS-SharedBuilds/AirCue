"""AirCue Streamlit Interactive Exploration & LLM Testing Interface."""
from __future__ import annotations

import asyncio
import io
import os
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from gtts import gTTS

from aircue.data.store import load_latest_snapshot
from aircue.llm.openrouter import OpenRouterClient
from aircue.llm.parsing import parse_json_robust
from aircue.llm.prompts import (
    SYSTEM_PROMPT_ANNOUNCEMENT,
    SYSTEM_PROMPT_DECISION,
    build_announcement_user_prompt,
    build_decision_user_prompt,
)
from aircue.llm.validators import validate_announcement
from aircue.messages.builder import build_message
from aircue.trigger.aqi import aqi_to_category_cpcb
from aircue.trigger.engine import Event

load_dotenv()

st.set_page_config(
    page_title="AirCue: Outdoor AQI & LLM Web Interface",
    page_icon="🎙️",
    layout="wide",
)

st.title("AirCue: Outdoor School Voice Announcer & LLM Testbed")
st.markdown(
    "Event-driven outdoor air-quality voice alert system for schools. "
    "Explore physical monitoring stations across Madhya Pradesh, test deterministic speech triggers, "
    "and interactively evaluate live LLM generation via OpenRouter."
)

tab_overview, tab_llm_announcement, tab_llm_decision, tab_benchmark, tab_clips = st.tabs([
    "📊 MP AQI Telemetry",
    "🤖 LLM Spoken Announcement Generator",
    "🧠 LLM Trigger Decision Engine",
    "📈 Benchmark Suite & Quota",
    "🎧 Pregenerated Audio Clips",
])

# -------------------------------------------------------------
# TAB 1: MP AQI Telemetry
# -------------------------------------------------------------
with tab_overview:
    st.subheader("Madhya Pradesh Ambient Air Quality Observations")
    try:
        df = load_latest_snapshot()
        df["dt"] = pd.to_datetime(df["timestamp"])
    except Exception as e:
        st.error(f"Failed to load dataset snapshot: {e}")
        st.stop()

    col_side1, col_side2 = st.columns([1, 2])
    locations = sorted(df["location"].unique().tolist())
    indore_index = locations.index("Vijay Nagar Scheme-78, Indore - Glenmark") if "Vijay Nagar Scheme-78, Indore - Glenmark" in locations else 0
    selected_loc = col_side1.selectbox("Select Station / Locality", locations, index=indore_index)

    loc_df = df[df["location"] == selected_loc].sort_values(by="dt")
    dataset_kind = loc_df["dataset_kind"].iloc[0] if not loc_df.empty and "dataset_kind" in loc_df.columns else "unknown"
    provider = loc_df["provider"].iloc[0] if not loc_df.empty and "provider" in loc_df.columns else "unknown"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Telemetry Type", "Physical Station" if dataset_kind == "measured_station" else "Atmospheric Model")
    m2.metric("Provider", str(provider).upper())
    m3.metric("Latest CPCB AQI", f"{loc_df['cpcb_aqi'].iloc[-1]:.0f}" if not loc_df.empty else "N/A")
    m4.metric("Mean PM2.5", f"{loc_df['pm2_5'].mean():.1f} µg/m³" if not loc_df.empty else "N/A")

    fig = px.line(
        loc_df,
        x="dt",
        y="cpcb_aqi",
        title=f"CPCB National AQI Timeline: {selected_loc}",
        labels={"dt": "Date & Time (IST)", "cpcb_aqi": "CPCB AQI"},
    )
    fig.add_hrect(y0=0, y1=50, line_width=0, fillcolor="green", opacity=0.1, annotation_text="Good (0-50)")
    fig.add_hrect(y0=51, y1=100, line_width=0, fillcolor="lightgreen", opacity=0.1, annotation_text="Satisfactory (51-100)")
    fig.add_hrect(y0=101, y1=200, line_width=0, fillcolor="yellow", opacity=0.1, annotation_text="Moderate (101-200)")
    fig.add_hrect(y0=201, y1=300, line_width=0, fillcolor="orange", opacity=0.1, annotation_text="Poor (201-300)")
    fig.add_hrect(y0=301, y1=400, line_width=0, fillcolor="red", opacity=0.1, annotation_text="Very Poor (301-400)")
    fig.add_hrect(y0=401, y1=500, line_width=0, fillcolor="darkred", opacity=0.1, annotation_text="Severe (401-500)")
    st.plotly_chart(fig, use_container_width=True)

# -------------------------------------------------------------
# TAB 2: LLM Spoken Announcement Generator
# -------------------------------------------------------------
with tab_llm_announcement:
    st.subheader("Test Spoken Announcement Generation via OpenRouter")
    st.caption("Deterministic air quality triggers select when to speak; LLM generates outdoor-tailored phrasing complying with strict safety constraints.")

    col_llm_cfg1, col_llm_cfg2 = st.columns([1, 1])

    with col_llm_cfg1:
        st.markdown("##### 1. Model & Provider Settings")
        openrouter_models = [
            "deepseek/deepseek-chat",
            "moonshotai/kimi-k3",
            "meta-llama/llama-3.3-70b-instruct",
            "qwen/qwen-2.5-72b-instruct",
            "mistralai/mistral-small-3.2-24b-instruct",
            "google/gemma-4-31b-it:free",
        ]
        chosen_model = st.selectbox("OpenRouter Model", openrouter_models, index=0)
        api_key_input = st.text_input(
            "OpenRouter API Key",
            value=os.environ.get("OPENROUTER_API_KEY", ""),
            type="password",
            help="Defaults to OPENROUTER_API_KEY from environment or .env",
        )
        temp = st.slider("Temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.05)

    with col_llm_cfg2:
        st.markdown("##### 2. School Environment & Sensor Context")
        alert_level = st.selectbox("CPCB Alert Severity", [1, 2, 3, 4], index=2, format_func=lambda x: {
            1: "Level 1: Moderate (AQI 101-200)",
            2: "Level 2: Poor (AQI 201-300)",
            3: "Level 3: Very Poor (AQI 301-400)",
            4: "Level 4: Severe (AQI 401+)",
        }[x])
        aqi_val = st.number_input("Simulated AQI", min_value=1, max_value=500, value=245)
        pm25_val = st.number_input("PM2.5 Concentration (µg/m³)", min_value=1.0, max_value=500.0, value=115.0)
        school_slot = st.selectbox("Timetable Slot", ["Sports PT / Physical Training", "Morning Assembly", "Recess / Lunch", "Dismissal / Gate", "General Campus"])
        target_language = st.radio("Language", ["Hindi (hi)", "English (en)"], horizontal=True)
        lang_code = "hi" if "Hindi" in target_language else "en"

    facts = {
        "level": alert_level,
        "category": aqi_to_category_cpcb(aqi_val),
        "aqi": aqi_val,
        "pm25": pm25_val,
        "site": "School Campus, Madhya Pradesh",
        "activity_slot": school_slot,
        "language": lang_code,
        "tone": "authoritative and polite",
    }

    st.markdown("---")
    if st.button("🚀 Generate Spoken Alert via LLM", type="primary"):
        if not api_key_input:
            st.error("Please provide an OpenRouter API Key in the sidebar or .env file.")
        else:
            with st.spinner(f"Querying {chosen_model} on OpenRouter..."):
                client = OpenRouterClient(model=chosen_model, api_key=api_key_input)
                prompt = build_announcement_user_prompt(facts)

                async def execute_query() -> Any:
                    return await client.complete(
                        prompt,
                        system_prompt=SYSTEM_PROMPT_ANNOUNCEMENT,
                        temperature=temp,
                        max_tokens=250,
                    )

                result = asyncio.run(execute_query())

                if result.raw_error:
                    st.error(f"OpenRouter API Error: {result.raw_error}")
                else:
                    st.success(f"Response received in **{result.latency_s:.2f} seconds**")
                    st.markdown("### Generated Announcement")
                    st.info(f"🎙️ **\"{result.text.strip()}\"**")

                    # Safety & Compliance Validation
                    st.markdown("#### Safety & Structural Validation Audit")
                    val = validate_announcement(result.text, expected_lang=lang_code, input_facts=facts)

                    v_cols = st.columns(6)
                    v_cols[0].metric("Word Limit (≤22)", "✅ Pass" if val.rule_results["word_limit"] else "❌ Fail")
                    v_cols[1].metric("Sentence Count (1-2)", "✅ Pass" if val.rule_results["sentence_count"] else "❌ Fail")
                    v_cols[2].metric("No Indoor Advice", "✅ Pass" if val.rule_results["no_indoor_ventilation"] else "❌ Fail")
                    v_cols[3].metric("No Medical Panic", "✅ Pass" if val.rule_results["no_medical_scare"] else "❌ Fail")
                    v_cols[4].metric("Script / Language", "✅ Pass" if val.rule_results["language_script"] else "❌ Fail")
                    v_cols[5].metric("No Fact Hallucination", "✅ Pass" if val.rule_results["no_hallucinated_digits"] else "❌ Fail")

                    if not val.passed:
                        st.warning(f"Validation Violations: {', '.join(val.failure_reasons)}")
                    else:
                        st.success("All safety and outdoor compliance rules passed!")

                    # Live Voice Synthesis Preview
                    st.markdown("#### Spoken Voice Audio (TTS Preview)")
                    try:
                        tts = gTTS(text=result.text.strip(), lang=lang_code)
                        buf = io.BytesIO()
                        tts.write_to_fp(buf)
                        buf.seek(0)
                        st.audio(buf, format="audio/mp3")
                    except Exception as err:
                        st.caption(f"TTS audio playback note: {err}")

# -------------------------------------------------------------
# TAB 3: LLM Trigger Decision Engine
# -------------------------------------------------------------
with tab_llm_decision:
    st.subheader("Test LLM Zero-Shot Trigger Decision (Task 2)")
    st.caption("AirCue's production engine uses a 100% deterministic state machine. In Task 2 of our benchmark, we evaluate whether LLMs can reliably parse multi-hour telemetry windows and output structured trigger JSON.")

    dec_model = st.selectbox("Decision Model", ["deepseek/deepseek-chat", "moonshotai/kimi-k3", "meta-llama/llama-3.3-70b-instruct", "qwen/qwen-2.5-72b-instruct"], key="dec_model")
    st.markdown("##### Simulated 6-Hour Particulate Trajectory")

    default_history = [
        {"timestamp": "07:00", "pm2_5": 35.0, "cpcb_aqi": 85},
        {"timestamp": "08:00", "pm2_5": 58.0, "cpcb_aqi": 125},
        {"timestamp": "09:00", "pm2_5": 85.0, "cpcb_aqi": 185},
        {"timestamp": "10:00", "pm2_5": 115.0, "cpcb_aqi": 240},
        {"timestamp": "11:00", "pm2_5": 130.0, "cpcb_aqi": 270},
        {"timestamp": "12:00", "pm2_5": 145.0, "cpcb_aqi": 295},
    ]

    hist_df = pd.DataFrame(default_history)
    st.dataframe(hist_df, use_container_width=True)

    if st.button("Evaluate Decision via LLM", type="primary"):
        client = OpenRouterClient(model=dec_model, api_key=os.environ.get("OPENROUTER_API_KEY", ""))
        dec_prompt = build_decision_user_prompt(default_history, {"level": 0, "minutes_since_last": 120})

        with st.spinner("Evaluating trajectory..."):
            async def run_dec() -> Any:
                return await client.complete(dec_prompt, system_prompt=SYSTEM_PROMPT_DECISION, temperature=0.0)

            dec_res = asyncio.run(run_dec())

            if dec_res.raw_error:
                st.error(f"Error: {dec_res.raw_error}")
            else:
                st.markdown("##### Raw Output")
                st.code(dec_res.text)
                parsed = parse_json_robust(dec_res.text)
                if parsed:
                    st.success("Valid JSON Decision Parsed:")
                    st.json(parsed)
                else:
                    st.error("Failed to parse valid JSON from LLM response.")

# -------------------------------------------------------------
# TAB 4: Benchmark Suite & Quota
# -------------------------------------------------------------
with tab_benchmark:
    st.subheader("LLM Benchmark Status & Quota Utilization")
    quota_path = Path("results/quota.json")
    if quota_path.exists():
        import json
        with open(quota_path) as f:
            quota_data = json.load(f)
        st.json(quota_data)
    else:
        st.info("No benchmark quota state found at `results/quota.json`. Run `aircue benchmark run` to execute.")

    summary_path = Path("results/report/summary.md")
    if summary_path.exists():
        st.markdown("### Benchmark Performance Summary")
        with open(summary_path, encoding="utf-8") as f:
            st.markdown(f.read())

# -------------------------------------------------------------
# TAB 5: Audio Clips Tester
# -------------------------------------------------------------
with tab_clips:
    st.subheader("Pregenerated Production Speech Clips (Offline Fallback)")
    st.caption("AirCue maintains 200 pre-synthesized WAV clips with cryptographic SHA-256 validation to ensure zero-latency failover when networks are offline.")

    c1, c2, c3 = st.columns(3)
    p_level = c1.selectbox("Alert Level", [1, 2, 3, 4], index=1, key="clip_lvl")
    p_lang = c2.selectbox("Language", ["en", "hi"], index=0, key="clip_lang")
    p_slot = c3.selectbox("Slot", ["general", "assembly", "sports_pt", "recess", "dismissal"], index=0, key="clip_slot")

    slot_param = None if p_slot == "general" else p_slot
    ev_obj = Event(kind="escalate", level=p_level, timestamp=0.0, aqi=250.0)
    built_msg = build_message(ev_obj, language=p_lang, slot=slot_param)

    st.info(f"**Synthesized Announcement:** {built_msg.text}")
    c_path = Path("clips") / f"{built_msg.clip_id}.wav"
    if c_path.exists():
        st.audio(str(c_path))
        st.caption(f"Audio file: `{c_path}`")
    else:
        st.warning(f"Clip `{built_msg.clip_id}.wav` not found in `clips/`. Run `aircue clips build`.")
