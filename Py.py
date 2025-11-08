# traffic_streamlit.py
# ------------------------------------------------------------
# Red Light Idle Emissions — Streamlit version of your Pygame app
# Controls are in the left sidebar. Use Run/Pause for continuous updates.

#streamlit run traffic_streamlit.py

# ------------------------------------------------------------

import time
import math
import pandas as pd
import streamlit as st

# -------------------- Page setup --------------------
st.set_page_config(page_title="Red Light Idle Emissions", page_icon="🚦", layout="wide")

# -------------------- Constants (ported from pygame) --------------------
ASSUME_CNG_FLEET = False  # kept for parity; not used directly
FPS = 60

# Colors (for labels only)
COLOR_CO2 = "#58C759"   # (88, 199, 89)
COLOR_CO  = "#FF9178"   # (255, 145, 120)
COLOR_O2  = "#78B4FF"   # (120, 180, 255)

# Simulation parameters (same as your code)
CO2_PER_VEH = 2.5
CO_PER_VEH  = 1.6
O2_CONSUME_PER_VEH = 0.8
DECAY_CO2 = 1.1
DECAY_CO  = 0.9
RECOVER_O2 = 0.8
SLOW_DECAY = 0.05

# -------------------- Helpers --------------------
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def init_state():
    """Initialize Streamlit session_state once."""
    if "initialized" in st.session_state:
        return
    s = st.session_state
    s.is_red = True
    s.vehicles = 12

    # gas levels / baselines
    s.level_co2 = 0.0
    s.level_co  = 0.0
    s.level_o2  = 100.0
    s.baseline_co2 = 0.0
    s.baseline_co  = 0.0
    s.baseline_o2  = 100.0

    # timing & run mode
    s.prev_ts = time.time()
    s.running = True

    s.initialized = True

def update_state(dt):
    """Port of your update() function using session_state."""
    s = st.session_state
    if s.is_red:
        s.level_co2 += s.vehicles * CO2_PER_VEH * dt
        s.level_co  += s.vehicles * CO_PER_VEH  * dt
        s.level_o2  -= s.vehicles * O2_CONSUME_PER_VEH * dt
        s.level_o2 = clamp(s.level_o2, 0, 100)

        # slow settling toward baselines even on red
        s.level_co2 = max(s.baseline_co2, s.level_co2 - SLOW_DECAY * dt)
        s.level_co  = max(s.baseline_co,  s.level_co  - SLOW_DECAY * dt)
    else:
        def decay(v, b, r):
            return b if v <= b else max(b, v - r * dt)

        s.level_co2 = decay(s.level_co2, s.baseline_co2, DECAY_CO2 * (1 + s.vehicles * 0.02))
        s.level_co  = decay(s.level_co,  s.baseline_co,  DECAY_CO  * (1 + s.vehicles * 0.02))
        s.level_o2  = clamp(s.level_o2 + RECOVER_O2 * dt * (1 + s.vehicles * 0.05), 0, 100)

def traffic_light_badge(is_red: bool):
    color = "#FF3B30" if is_red else "#34C759"
    label = "RED" if is_red else "GREEN"
    return f"""
    <div style="
        display:inline-flex;align-items:center;gap:8px;
        padding:6px 10px;border-radius:999px;
        background:#1e1e24;border:1px solid #2a2a35;color:#fff;">
        <span style="width:12px;height:12px;border-radius:50%;display:inline-block;background:{color};"></span>
        <span style="font-weight:600;letter-spacing:.4px;">{label}</span>
    </div>
    """

def scaled_bar(value, gas):
    """Match your visual scaling: CO2/CO saturate, O2 is direct percentage."""
    if gas == "Fresh O2":
        return clamp(value, 0, 100)
    # Saturating mapping like: BAR_MAX_HEIGHT * (1 - exp(-level/40))
    sat = 100 * (1.0 - math.exp(-value / 40.0))
    return clamp(sat, 0, 100)

# -------------------- App --------------------
init_state()
s = st.session_state

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    s.is_red = st.toggle("Red light (idle)", value=s.is_red, help="Toggle to simulate red/green.")
    s.vehicles = st.slider("Vehicles waiting", 0, 99, s.vehicles, help="Number of vehicles at the signal.")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Run" if not s.running else "Pause"):
            s.running = not s.running
    with c2:
        if st.button("Step 0.2s"):
            update_state(0.2)
    with c3:
        if st.button("Reset"):
            s.level_co2 = 0.0
            s.level_co  = 0.0
            s.level_o2  = 100.0
            s.baseline_co2 = 0.0
            s.baseline_co  = 0.0
            s.baseline_o2  = 100.0

    st.caption("Use **Run/Pause** for continuous updates, or **Step** to advance once.")

# Header & status
st.markdown("## 🚦 Red Light Idle Emissions (Streamlit)")
st.markdown(traffic_light_badge(s.is_red), unsafe_allow_html=True)
st.write(f"**Vehicles:** {s.vehicles}")

# Compute dt and advance if running
now = time.time()
dt = now - s.prev_ts
dt = clamp(dt, 0.0, 0.25)  # avoid huge jumps on first load/tab wake
s.prev_ts = now

if s.running:
    update_state(dt)
    # gentle auto-refresh ~10fps without hacks
    time.sleep(0.1)
    st.rerun()

# Data for display
data = [
    {"Gas": "CO2",       "Level": s.level_co2, "Scaled": scaled_bar(s.level_co2, "CO2"),       "Color": COLOR_CO2},
    {"Gas": "CO",        "Level": s.level_co,  "Scaled": scaled_bar(s.level_co,  "CO"),        "Color": COLOR_CO},
    {"Gas": "Fresh O2",  "Level": s.level_o2,  "Scaled": scaled_bar(s.level_o2, "Fresh O2"),   "Color": COLOR_O2},
]
df = pd.DataFrame(data)

left, right = st.columns([1.2, 1], vertical_alignment="start")

with left:
    st.subheader("Idle Emissions — Bar Graph")
    # We plot the scaled values (0–100) for a consistent visual range
    st.bar_chart(
        df.set_index("Gas")["Scaled"],
        height=360,
        use_container_width=True,
    )
    st.dataframe(
        df[["Gas", "Level"]].rename(columns={"Level": "Current Value"}),
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.subheader("How it works")
    st.markdown(
        """
        - **RED**: Vehicles idle → CO₂ and CO rise; fresh O₂ falls (consumption).
        - **GREEN**: Traffic flows → CO₂ and CO decay; O₂ recovers.
        - Bars:
          - **CO₂/CO** use a saturating scale for readability at high values.
          - **Fresh O₂** displays as a direct percentage (0–100).
        """
    )
    st.caption("Model constants: CO₂/veh=2.5, CO/veh=1.6, O₂ use/veh=0.8; decay/recovery tuned for demo.")

st.divider()
st.caption("Tip: If the page seems stuck, click **Run** in the sidebar or hard-refresh (Cmd+Shift+R).")
