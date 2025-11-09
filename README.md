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
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the Streamlit app:
   ```bash
   streamlit run traffic_streamlit.py
   ```

### Option 2 — Run Online (Streamlit Cloud)
You can also deploy it directly to [Streamlit Cloud](https://streamlit.io/cloud) —  
just upload the files and click **Deploy**.

---

## 📊 Simulation Parameters
| Parameter | Description | Default |
|------------|-------------|----------|
| Vehicles | Number of idling vehicles | 12 |
| CO₂ per vehicle | Rate of emission per second | 2.5 units |
| CO per vehicle | Rate of emission per second | 1.6 units |
| O₂ consumption | O₂ consumed per vehicle | 0.8 units |
| Recovery rate | O₂ recovery during GREEN | 0.8 units |
| Decay rate | Rate of CO/CO₂ dispersion | 0.9–1.1 units |

---

## 🌱 Future Enhancements
- Integrate **real-time traffic or emission data**.
- Display **historical pollution graphs**.
- Add **CNG fleet simulation** toggle.
- Export simulation data to CSV.

---

## 🧑‍💻 Author
**Umesh Chandra Karthikeya**  
Founder & CEO — Acintyo Group  
🌐 [karthikeya.koduru07@icloud.com]

---

## 📜 License
This project is licensed under the MIT License — feel free to use, modify, and share responsibly.

---
