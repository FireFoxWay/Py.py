# traffic_streamlit.py

#streamlit run traffic_streamlit.py

import time
import math
import pandas as pd
import streamlit as st

# -------------------- Page setup --------------------
st.set_page_config(page_title="Red Light Idle Emissions", page_icon="🚦", layout="wide")

# -------------------- Constants (ported from pygame) --------------------
ASSUME_CNG_FLEET = False  # kept for parity; not used in this simple port
FPS = 60

# Colors (used for styling/legend only)
COLOR_CO2 = "#58C759"   # (88, 199, 89)
COLOR_CO  = "#FF9178"   # (255, 145, 120)
COLOR_O2  = "#78B4FF"   # (120, 180, 255)

# Simulation parameters
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

def update_state(dt):
    """Port of your update() function that mutates session_state levels."""
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

def init_state():
    if "initialized" in st.session_state:
        return
    s = st.session_state
    s.is_red = True
    s.vehicles = 12

    # gas levels
    s.level_co2 = 0.0
    s.level_co  = 0.0
    s.level_o2  = 100.0

    s.baseline_co2 = 0.0
    s.baseline_co  = 0.0
    s.baseline_o2  = 100.0

    # timing
    s.prev_ts = time.time()
    s.running = True  # auto-update on load
    s.initialized = True

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

# -------------------- App --------------------
init_state()
s = st.session_state

# Left controls
with st.sidebar:
    st.header("Controls")
    s.is_red = st.toggle("Red light (idle)", value=s.is_red, help="Toggle to simulate red/green.")
    s.vehicles = st.slider("Vehicles waiting", 0, 99, s.vehicles, help="Number of vehicles at the signal.")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    with col_btn1:
        if st.button("Run" if not s.running else "Pause"):
            s.running = not s.running
    with col_btn2:
        if st.button("Step 0.2s"):
            # single step advance
            update_state(0.2)
    with col_btn3:
        if st.button("Reset"):
            # reset levels & baselines
            s.level_co2 = 0.0
            s.level_co  = 0.0
            s.level_o2  = 100.0
            s.baseline_co2 = 0.0
            s.baseline_co  = 0.0
            s.baseline_o2  = 100.0

    st.caption("Press **Space** effect from Pygame is replaced by the toggle above.\n"
               "Use **Run/Pause** for continuous updates or **Step** for discrete updates.")

# Header
st.markdown("## 🚦 Red Light Idle Emissions (Streamlit)")
st.markdown(traffic_light_badge(s.is_red), unsafe_allow_html=True)
st.write(f"**Vehicles:** {s.vehicles}")

# Timing and update
now = time.time()
dt = now - s.prev_ts
# Avoid huge jumps on first load or tab wake-ups
dt = clamp(dt, 0.0, 0.25)
s.prev_ts = now

if s.running:
    update_state(dt)
    # gentle auto-refresh (about 10 FPS feels fine for UI)
    st.experimental_set_query_params(_=str(now))  # keeps URL changing slightly to avoid caching
    st.autorefresh = st.experimental_rerun  # alias for clarity (Streamlit reruns the script)

# ---- Display: Bars ----
# For CO2/CO we use a saturating scale like your exp() mapping; O2 is direct percentage.
def scaled_bar_height(value, gas):
    if gas == "Fresh O2":
        return clamp(value, 0, 100)
    # mimic your saturation: BAR_MAX_HEIGHT * (1 - exp(-level/40)), normalized to 0..100
    sat = 100 * (1.0 - math.exp(-value / 40.0))
    return clamp(sat, 0, 100)

data = [
    {"Gas": "CO2", "Level": s.level_co2, "Scaled": scaled_bar_height(s.level_co2, "CO2"), "Color": COLOR_CO2},
    {"Gas": "CO",  "Level": s.level_co,  "Scaled": scaled_bar_height(s.level_co,  "CO"),  "Color": COLOR_CO},
    {"Gas": "Fresh O2", "Level": s.level_o2,  "Scaled": scaled_bar_height(s.level_o2, "Fresh O2"), "Color": COLOR_O2},
]
df = pd.DataFrame(data)

left, right = st.columns([1.2, 1], vertical_alignment="start")

with left:
    st.subheader("Idle Emissions — Bar Graph")
    # Simple bar rendering using st.bar_chart (uses Scaled for consistent visual range)
    st.bar_chart(
        df.set_index("Gas")["Scaled"],
        height=360,
        use_container_width=True,
    )
    # Show actual values below
    st.dataframe(
        df[["Gas", "Level"]].rename(columns={"Level": "Current Value"}),
        use_container_width=True,
        hide_index=True,
    )

with right:
    st.subheader("How it works")
    st.markdown(
        """
        - **RED**: Vehicles idle → CO₂ and CO increase; fresh O₂ decreases (consumption).
        - **GREEN**: Traffic flows → CO₂ and CO decay; O₂ recovers.
        - Bars:
          - **CO₂/CO** use a saturating display scale (not linear) to stay readable as values grow.
          - **Fresh O₂** shows percent 0–100.
        - Use the sidebar to toggle Red/Green, change vehicle count, **Run/Pause**, or **Step**.
        """
    )
    st.caption("Model constants: CO₂/veh=2.5, CO/veh=1.6, O₂ use/veh=0.8, decay/recovery tuned for demo.")

st.divider()
st.caption("Tip: If the page looks frozen, click **Run** in the sidebar or hard refresh (Cmd+Shift+R).")
