# 🏁 AI Virtual Drag Race Simulator

A fun and interactive **AI-powered drag race simulator** built using **Streamlit**, where you can select real-world vehicles available in India and simulate a quarter-mile race between them.

---

## 🚀 Features

* 🏎 Compare **two vehicles** in a virtual drag race
* 🤖 Powered by AI to estimate:

  * Engine specs
  * Power-to-weight ratio
  * Acceleration
  * Quarter-mile time
* 📊 **Race visualization** using progress bars
* 🎮 **Animated drag race simulation**
* 🔁 Replay race animation
* 🇮🇳 Covers vehicles **currently in production in India**

---

## 🚗 Supported Vehicle Types

The simulator includes a wide dataset of Indian vehicles:

* 🏍 **Bikes**
* 🛵 **Scooters (Petrol + EV)**
* 🚗 **Cars (Budget → Luxury → EV)**
* 🚌 **Buses**
* 🚚 **Trucks**

---

## 🧠 How It Works

1. Select two vehicles
2. AI analyzes:

   * Performance specs
   * Acceleration metrics
3. AI predicts:

   * Quarter-mile times
   * Race winner
4. App displays:

   * 📊 Visualization
   * 🏁 Animated race

---

## 🛠 Tech Stack

* **Frontend & UI:** Streamlit
* **AI Engine:** OpenAI (via API)
* **Backend Logic:** Python
* **Data Source:** Custom JSON dataset (Indian vehicles)

---

## 📂 Project Structure

```
drag-race-ai/
│
├── app.py
├── vehicles_india.json
├── requirements.txt
├── .gitignore
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/SaurabhLP88/drag-race-ai.git
cd drag-race-ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add API key (Streamlit Secrets)

Create `.streamlit/secrets.toml`:

```toml
GITHUB_TOKEN = "your_api_key_here"
```

### 4. Run the app

```bash
streamlit run app.py
```

---

## 🌐 Deployment

You can deploy this app easily on:

👉 **Streamlit Cloud (streamlit.app)**

---

## ⚠️ Notes

* AI responses may vary slightly each run
* Vehicle specs are estimated based on available data
* Ensure API key is kept secure (do not upload `.env`)

---

## 📌 Future Improvements

* 🏎 Real car animations (instead of emojis)
* 📊 Leaderboard of fastest vehicles
* 🎮 Multiplayer race mode
* 📱 Mobile optimization
* 💾 Save race history

---

## 👨‍💻 Author

Built as a mini project to explore:

* AI + UI integration
* Real-world vehicle datasets
* Interactive simulations

---

## ⭐ If you like this project

Give it a ⭐ on GitHub and feel free to contribute!
