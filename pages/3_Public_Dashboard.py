"""
Public dashboard: live map, hotspot heat map, statistics and SDG impact.
"""
from datetime import datetime

import folium
import pandas as pd
import streamlit as st
from folium.plugins import HeatMap
from streamlit_folium import st_folium

import config
from core import db, logic

st.set_page_config(page_title="Public Dashboard", page_icon="📊", layout="wide")
db.init_db()
logic.refresh_all()

st.title("📊 Public Dashboard")

issues = db.all_issues()
if not issues:
    st.info("No reports yet. Go to **Report Problem** to add the first one.")
    st.stop()

df = pd.DataFrame(issues)
resolved = df[df.status == "Resolved"]

# ---------- Headline numbers ----------
def avg_fix_hours(rows):
    times = [(datetime.fromisoformat(r.resolved_at) - datetime.fromisoformat(r.created_at)).total_seconds() / 3600
             for r in rows.itertuples() if r.resolved_at]
    return sum(times) / len(times) if times else None

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total issues", len(df))
c2.metric("Open", int((df.status != "Resolved").sum()))
c3.metric("Resolved", len(resolved))
c4.metric("Escalated", int(((df.escalated == 1) & (df.status != "Resolved")).sum()))
fix = avg_fix_hours(resolved)
c5.metric("Avg. time to fix", f"{fix:.1f} h" if fix is not None else "–")

# ---------- Maps ----------
colour = {"Open": "red", "In progress": "orange", "Resolved": "green"}
tab1, tab2, tab3 = st.tabs(["Live issue map", "Hotspot heat map", "Women's safety map"])

with tab1:
    m = folium.Map(location=config.MAP_CENTER, zoom_start=config.MAP_ZOOM)
    for r in df.itertuples():
        folium.Marker(
            (r.latitude, r.longitude),
            tooltip=f"#{r.id} {r.category} – {r.status}",
            popup=f"#{r.id} {r.category}<br>Severity {r.severity}<br>{r.report_count} report(s)",
            icon=folium.Icon(color=colour.get(r.status, "blue")),
        ).add_to(m)
    st_folium(m, height=420, use_container_width=True, key="live_map")
    st.caption("🔴 Open  🟠 In progress  🟢 Resolved")

with tab2:
    m2 = folium.Map(location=config.MAP_CENTER, zoom_start=config.MAP_ZOOM)
    HeatMap([(r.latitude, r.longitude, r.report_count) for r in df.itertuples()], radius=25).add_to(m2)
    st_folium(m2, height=420, use_container_width=True, key="heat_map")
    st.caption("Red areas have the most reports: places that need regular attention.")

with tab3:
    dark = df[df.category == "Dark / unsafe spot"]
    m3 = folium.Map(location=config.MAP_CENTER, zoom_start=config.MAP_ZOOM)
    for r in dark.itertuples():
        folium.CircleMarker((r.latitude, r.longitude), radius=12, color="purple", fill=True,
                            tooltip=f"Unsafe / dark spot – {r.status}").add_to(m3)
    st_folium(m3, height=420, use_container_width=True, key="safety_map")
    st.caption(f"{len(dark)} dark or unsafe spot(s) reported.")

# ---------- Charts ----------
left, right = st.columns(2)
with left:
    st.subheader("Issues by category")
    st.bar_chart(df.groupby("category").size())
with right:
    st.subheader("Issues by department and status")
    st.bar_chart(df.groupby(["department", "status"]).size().unstack(fill_value=0))

# ---------- SDG impact ----------
st.subheader("🌍 SDG impact (resolved issues)")
sdg_counts = {}
for r in resolved.itertuples():
    sdg = config.CATEGORIES[r.category]["sdg"]
    sdg_counts[sdg] = sdg_counts.get(sdg, 0) + 1
sdg_counts["SDG 11"] = len(resolved)   # every fix makes the community better
cols = st.columns(len(sdg_counts))
for col, (sdg, n) in zip(cols, sorted(sdg_counts.items())):
    col.metric(sdg, n)
