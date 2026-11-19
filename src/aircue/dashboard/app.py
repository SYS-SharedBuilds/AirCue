"""AirCue Streamlit Interactive Exploration Dashboard."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from aircue.data.store import load_latest_snapshot
from aircue.messages.builder import build_message
from aircue.trigger.engine import Event

st.set_page_config(page_title="AirCue Outdoor AQI Dashboard", layout="wide")

st.title("AirCue: Outdoor Air-Quality Voice Announcer Dashboard")
st.markdown("Interactive exploration of ambient particulate air quality, CPCB AQI levels, and announcement clips.")

# Load snapshot
try:
    df = load_latest_snapshot()
    df["dt"] = pd.to_datetime(df["timestamp"])
except Exception as e:
    st.error(f"Failed to load dataset snapshot: {e}")
    st.stop()

# Sidebar filters
cities = sorted(df["location"].unique().tolist())
selected_city = st.sidebar.selectbox("Select City", cities, index=cities.index("Indore") if "Indore" in cities else 0)

city_df = df[df["location"] == selected_city].sort_values(by="dt")

col1, col2, col3 = st.columns(3)
col1.metric("Total Records", f"{len(city_df):,}")
col2.metric("Mean PM2.5", f"{city_df['pm2_5'].mean():.1f} µg/m³")
col3.metric("Mean CPCB AQI", f"{city_df['cpcb_aqi'].mean():.1f}")

# Timeline Plot
st.subheader("AQI & Particulate Concentration Timeline")
fig = px.line(city_df, x="dt", y="cpcb_aqi", title=f"CPCB National AQI in {selected_city}")
fig.add_hrect(y0=0, y1=50, line_width=0, fillcolor="green", opacity=0.1, annotation_text="Good")
fig.add_hrect(y0=51, y1=100, line_width=0, fillcolor="lightgreen", opacity=0.1, annotation_text="Satisfactory")
fig.add_hrect(y0=101, y1=200, line_width=0, fillcolor="yellow", opacity=0.1, annotation_text="Moderate")
fig.add_hrect(y0=201, y1=300, line_width=0, fillcolor="orange", opacity=0.1, annotation_text="Poor")
fig.add_hrect(y0=301, y1=400, line_width=0, fillcolor="red", opacity=0.1, annotation_text="Very Poor")
fig.add_hrect(y0=401, y1=500, line_width=0, fillcolor="darkred", opacity=0.1, annotation_text="Severe")
st.plotly_chart(fig, use_container_width=True)

# Audio Clip Preview
st.subheader("Audio Clip & Announcement Tester")
test_col1, test_col2, test_col3 = st.columns(3)
test_level = test_col1.selectbox("Alert Level", [1, 2, 3, 4], index=1)
test_lang = test_col2.selectbox("Language", ["en", "hi"], index=0)
test_slot = test_col3.selectbox("Slot", ["general", "assembly", "sports_pt", "recess", "dismissal"], index=0)

slot_val = None if test_slot == "general" else test_slot
ev = Event(kind="escalate", level=test_level, timestamp=0.0, aqi=250.0)
msg = build_message(ev, language=test_lang, slot=slot_val)

st.info(f"**Synthesized Announcement:** {msg.text}")
clip_path = Path("clips") / f"{msg.clip_id}.wav"
if clip_path.exists():
    st.audio(str(clip_path))
else:
    st.warning("Clip not pre-built. Run `aircue clips build`.")
