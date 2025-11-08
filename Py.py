# traffic_streamlit.py
# ------------------------------------------------------------
# Red Light Idle Emissions — Streamlit (no experimental APIs)
# Works on older Streamlit versions. No st.experimental_rerun.
# ------------------------------------------------------------

import time
import math
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Red Light Idle Emissions", page_icon="🚦", layout="wide")

# ---------- Constants ----------
COLOR_CO2 = "#58C759"   # (88, 199, 89)
COLOR_CO  = "#FF9178"   # (255, 145, 120)
COLOR_O2  = "#78B4FF"   # (120, 180, 255)

CO2_PER_VEH = 2.5
CO_PER_VEH  = 1.6
O2_CONSUME_PER_VEH = 0.8
DECAY_CO2 = 1.1
DECAY_CO  = 0.9
RECOVER_O2 = 0.8
SLOW_DECAY = 0.05

def clamp(x, lo, hi): 
    return max(lo, min(hi, x))

def init_state():
    if "initialized" in st.session_state:
        return
    s = st.session_state
    s.is_red = True
    s.vehicles = 12

    # levels & baselines
    s.level_co2 = 0.0
    s.level_co  = 0.0
    s.level_o2  = 100.0
    s.baseline_co2 = 0.0
    s.baseline_co  = 0.0
    s.baseline_o2  = 100.0

    # timing
    s.prev_ts = time.time()

    s.initialized = True

def update_state(dt):
    s = st.session_state
    if s.is_red:
        s.level_co2 += s.vehicles * CO2_PER_VEH * dt
        s.level_co  += s.vehicles * CO_PER_VEH  * dt
        s.level_o2  -= s.vehicles * O2_CONSUME_PER_VEH * dt
        s.level_o2 = clamp(s.level_o2, 0, 100)

        # slow settle even on red
        s.level_co2 = max(s.baseline_co2, s.level_co2 - SLOW_DECAY * dt)
        s.level_co  = max(s.baseline_co,  s.level_co  - SLOW_DECAY * dt)
    else:
        def decay(v, b, r): 
            return b if v <= b else max(b, v - r * dt)
        s.level_co2 = decay(s.level_co2, s.baseline_co2, DECAY_CO2 * (1 + s.vehicles * 0.02))
        s.level_co  = decay(s.level_co,  s.baseline_co,  DECAY_CO  * (1 + s.vehicles * 0.02))
        s.level_o2  = clamp(s.level_o2 + RECOVER_O2 * dt * (1 + s.vehicles * 0.05), 0, 100)

def badge(is_red: bool):
    color = "#FF3B30" if is_red else "#34C759"
    label = "RED" if is_red else "GREEN"
    return f"""
    <div style="display:inline-flex;align-items:center;gap:8px;padding:6px 10px;border-radius:999px;background:#1e1e24;border:1px solid #2a2a35;color:#fff;">
      <span style="width:12px;height:12px;border-radius:50%;display:inline-block;background:{color};"></span>
      <span style="font-weight:600;letter-spacing:.4px;">{label}</span>
    </div>
    """

def scaled_bar(value, gas):
    # CO2/CO: saturating mapping like your pygame (1 - exp(-level/40)) -> 0..100
    if gas == "Fresh O2":
        return clamp(value, 0, 100)
    return clamp(100 * (1.0 - math.exp(-value / 40.0)), 0, 100)

# ---------- App ----------
init_state()
s = st.session_state

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    s.is_red = st.toggle("Red light (idle)", value=s.is_red, help="Toggle red/green.")
    s.vehicles = st.slider("Vehicles waiting", 0, 99, s.vehicles, help="Number of vehicles at the signal.")

    st.markdown("**Update options**")
    colA, colB = st.columns(2)
    with colA:
        if st.button("Step 0.2s"):
            update_state(0.2)
    with colB:
        run_secs = st.number_input("Run seconds", min_value=1.0, max_value=60.0, value=5.0, step=0.5)
        if st.button("Run N seconds"):
            placeholder_chart = st.empty()
            placeholder_table = st.empty()
            start = time.time()
            last = start
            while time.time() - start < run_secs:
                now = time.time()
                dt = clamp(now - last, 0.0, 0.25)
                last = now
                update_state(dt)

                # draw during the loop (no rerun needed)
                df = pd.DataFrame([
                    {"Gas": "CO2",      "Level": s.level_co2, "Scaled": scaled_bar(s.level_co2, "CO2")},
                    {"Gas": "CO",       "Level": s.level_co,  "Scaled": scaled_bar(s.level_co,  "CO")},
                    {"Gas": "Fresh O2", "Level": s.level_o2,  "Scaled": scaled_bar(s.level_o2, "Fresh O2")},
                ]).set_index("Gas")
                placeholder_chart.bar_chart(df["Scaled"], height=360, use_container_width=True)
                placeholder_table.dataframe(
                    df[["Level"]].rename(columns={"Level": "Current Value"}),
                    use_container_width=True
                )
                time.sleep(0.1)

    st.markdown("---")
    auto = st.checkbox("Auto-refresh (every 0.5s)", help="Version-safe; reloads the page periodically.")
    if auto:
        # Compute dt since last run, update once, then instruct the browser to refresh after 0.5s.
        now = time.time()
        dt = clamp(now - s.prev_ts, 0.0, 0.25)
        s.prev_ts = now
        update_state(dt)
        # Safe, no Streamlit experimental API:
        st.markdown(
            "<meta http-equiv='refresh' content='0.5'>",
            unsafe_allow_html=True
        )
    else:
        # If not auto-refreshing, still keep prev_ts fresh for accurate future dt
        s.prev_ts = time.time()

st.markdown("## 🚦 Red Light Idle Emissions (Streamlit)")
st.markdown(badge(s.is_red), unsafe_allow_html=True)
st.write(f"**Vehicles:** {s.vehicles}")

# Draw current frame once (for Step mode, after Run N seconds ends, or each auto-refresh tick)
df_view = pd.DataFrame([
    {"Gas": "CO2",      "Level": s.level_co2, "Scaled": scaled_bar(s.level_co2, "CO2"),      "Color": COLOR_CO2},
    {"Gas": "CO",       "Level": s.level_co,  "Scaled": scaled_bar(s.level_co,  "CO"),       "Color": COLOR_CO},
    {"Gas": "Fresh O2", "Level": s.level_o2,  "Scaled": scaled_bar(s.level_o2, "Fresh O2"),  "Color": COLOR_O2},
])

left, right = st.columns([1.2, 1])

with left:
    st.subheader("Idle Emissions — Bar Graph")
    st.bar_chart(df_view.set_index("Gas")["Scaled"], height=360, use_container_width=True)
    st.dataframe(
        df_view[["Gas", "Level"]].rename(columns={"Level": "Current Value"}),
        use_container_width=True,
        hide_index=True
    )

with right:
    st.subheader("How it works")
    st.markdown("""
- **RED**: Vehicles idle → CO₂ and CO rise; Fresh O₂ falls.
- **GREEN**: Flow → CO₂ and CO decay; Fresh O₂ recovers.
- Bars: CO₂/CO use a saturating scale for readability; Fresh O₂ is a 0–100% scale.
""")
    st.caption("Constants: CO₂/veh=2.5, CO/veh=1.6, O₂ use/veh=0.8; decay/recovery tuned for demo.")

st.divider()
st.caption("Tip: For continuous motion, enable **Auto-refresh** or use **Run N seconds**.")
