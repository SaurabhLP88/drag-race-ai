import os
import streamlit as st
import json
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get token
token = os.getenv("GITHUB_TOKEN")

st.set_page_config(
    page_title="AI Drag Race Simulator",
    layout="wide"
)

st.title("🏁 AI Drag Race Simulator")
st.caption("Select two vehicles and simulate a quarter-mile drag race using AI.")

# Check if token exists
if not token:
    st.error("❌ GITHUB_TOKEN not found. Please check your .env file.")
    st.stop()

if "race_result" not in st.session_state:
    st.session_state.race_result = None

if "time1" not in st.session_state:
    st.session_state.time1 = None

if "time2" not in st.session_state:
    st.session_state.time2 = None

if "vehicle1" not in st.session_state:
    st.session_state.vehicle1 = None

if "vehicle2" not in st.session_state:
    st.session_state.vehicle2 = None

# Load Indian vehicle dataset
with open("vehicles_india.json", "r", encoding="utf-8") as f:
    vehicles = json.load(f)

def extract_times(text):

    numbers = re.findall(r"(\d+\.?\d*)\s*(?:seconds|sec|s)", text.lower())

    if len(numbers) >= 2:
        return float(numbers[0]), float(numbers[1])

    return None, None

def vehicle_selector(label):

    st.subheader(label)

    v_type = st.selectbox(
        "Vehicle Type",
        list(vehicles.keys()),
        key=label + "_type"
    )

    brands = list(vehicles[v_type].keys())

    brand = st.selectbox(
        "Brand",
        brands,
        key=label + "_brand"
    )

    models = list(vehicles[v_type][brand].keys())

    model = st.selectbox(
        "Model",
        models,
        key=label + "_model"
    )

    variants = vehicles[v_type][brand][model]

    variant = st.selectbox(
        "Variant",
        variants,
        key=label + "_variant"
    )

    vehicle_name = f"{brand} {model} {variant}"

    return vehicle_name

# User inputs
left, right = st.columns([1,3])

with left:

    vehicle1 = vehicle_selector("Vehicle 1")
    vehicle2 = vehicle_selector("Vehicle 2")

    simulate = st.button("Simulate Drag Race")

def run_animation(vehicle1, vehicle2, time1, time2):

    st.divider()
    st.subheader("🚦 Drag Race Animation")

    rerun = st.button("🔁 Rerun Animation")

    if rerun:
        st.rerun()

    track1 = st.empty()
    track2 = st.empty()

    finish = 50
    max_time = max(time1, time2)

    speed1 = max_time / time1
    speed2 = max_time / time2

    for i in range(finish + 1):

        progress1 = min((i / finish) * speed1, 1)
        progress2 = min((i / finish) * speed2, 1)

        pos1 = int(progress1 * finish)
        pos2 = int(progress2 * finish)

        track1.text(f"{vehicle1}\n🏎️{'─'*pos1}🏁")
        track2.text(f"{vehicle2}\n🏎️{'─'*pos2}🏁")

        time.sleep(0.05)

    winner = vehicle1 if time1 < time2 else vehicle2
    st.success(f"🏆 Winner: {winner}")


if simulate:

    # Prevent empty inputs
    if not vehicle1 or not vehicle2:
        st.warning("Please enter both vehicles.")
        st.stop()

    client = OpenAI(
        base_url="https://models.github.ai/inference",
        api_key=token
    )

    prompt = f"""
    You are an automotive performance analyst.

    Simulate a realistic quarter-mile drag race.

    Vehicle 1: {vehicle1}
    Vehicle 2: {vehicle2}

    Steps:
    1. Identify accurate engine specs
    2. Estimate power, torque, and weight
    3. Estimate 0-60 mph and 0-100 km/h acceleration
    4. Calculate power-to-weight ratio
    5. Estimate quarter mile time
    6. Predict the winner

    Output format:

    Vehicle Specs
    Vehicle 1
    Vehicle 2

    Performance
    0-60 km/h
    0-100 km/h
    Quarter Mile Results
    {vehicle1} Time: XX.X seconds
    {vehicle2} Time: XX.X seconds

    Winner
    Reason
    """

    with st.spinner("Simulating drag race... 🏁"):

        response = client.chat.completions.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=800
        )    

    result_text = response.choices[0].message.content

    st.session_state.race_result = result_text
    time1, time2 = extract_times(result_text)
    st.session_state.time1 = time1
    st.session_state.time2 = time2
    st.session_state.vehicle1 = vehicle1
    st.session_state.vehicle2 = vehicle2  

with right:
    if st.session_state.race_result:

        vehicle1 = st.session_state.vehicle1
        vehicle2 = st.session_state.vehicle2
        time1 = st.session_state.time1
        time2 = st.session_state.time2
        result_text = st.session_state.race_result

        if time1 is None or time2 is None:
            st.warning("⚠️ Could not extract quarter-mile times from AI response.")
            st.stop()

        st.success("Race Result")

        # -----------------------------
        # RACE VISUALIZATION FIRST
        # -----------------------------
        
        st.subheader("🏁 Quarter Mile Race Visualization")

        winner_time = min(time1, time2)

        progress1 = winner_time / time1
        progress2 = winner_time / time2

        st.write(vehicle1)
        st.progress(progress1)

        st.write(vehicle2)
        st.progress(progress2)

        # -----------------------------
        # ANIMATION
        # -----------------------------

        run_animation(vehicle1, vehicle2, time1, time2)

        # -----------------------------
        # AI ANALYSIS LAST
        # -----------------------------

        st.divider()
        st.subheader("📊 AI Race Analysis")

        st.write(result_text)