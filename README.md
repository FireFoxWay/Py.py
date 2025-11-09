# 🚦 Red Light Idle Emissions — Simulation (Python / Streamlit)

A simple yet interactive simulation that visualizes **vehicular gas emissions** during a red traffic signal.  
When vehicles are idling at a red light, **CO₂ and CO rise** while **fresh oxygen levels drop** — this project demonstrates that effect dynamically.

---

## 🎯 Purpose
This simulation highlights how idling vehicles contribute to air pollution and oxygen depletion, encouraging better traffic behavior and environmental awareness.

---

## 🧠 Concept
- When the **signal is RED**, vehicles idle, releasing gases:
  - **CO₂ (Carbon Dioxide)** increases.
  - **CO (Carbon Monoxide)** increases.
  - **O₂ (Oxygen)** decreases.
- When the **signal turns GREEN**, traffic flow resumes and:
  - **CO₂ and CO** gradually decrease (dispersion effect).
  - **O₂** recovers slowly in the environment.

---

## ⚙️ Features
- Dynamic bar graph visualization of CO₂, CO, and Fresh O₂ levels.  
- Adjustable number of vehicles waiting at the signal.  
- Toggle between **RED** (idle) and **GREEN** (moving) modes.  
- Optional auto-refresh to see real-time simulation changes.  
- Clean, modern UI built with **Streamlit**.

---

## 🛠️ Tech Stack
- **Python 3.9+**
- **Streamlit**
- **Pandas**
- **Math / Time libraries**

---

## ▶️ Run the Simulation

### Option 1 — Local Run
1. Clone this repository:
   ```bash
   git clone https://github.com/<your-username>/red-light-emissions.git
   cd red-light-emissions
