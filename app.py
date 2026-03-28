import os
import streamlit as st
import json
import re
import time
from openai import OpenAI
from dotenv import load_dotenv
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

# Convert images to base64
bg_image = get_base64_image("images/sunshine-01.jpg")
vs_image = get_base64_image("images/versus-01.png")

# Load environment variables
load_dotenv()

# Get token
# token = os.getenv("GITHUB_TOKEN")
try:
    token = os.getenv("GITHUB_TOKEN") or st.secrets.get("GITHUB_TOKEN")
except:
    token = None

st.set_page_config(
    page_title="AI Drag Race Simulator",
    layout="wide"
)

st.markdown(f"""
    <style>
    /* Full app background */
    [data-testid="stAppViewContainer"] {{
        background-image: url("data:image/jpg;base64,{bg_image}");
        background-attachment: initial; background-position: center; background-repeat: no-repeat;
        background-size: cover; color: black;
    }}

    /* Make content readable */
    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
    }}

    [data-testid="stToolbar"] {{
        right: 2rem;
    }}
            
    [data-testid="stWidgetLabel"] {{
        color: black;
    }}
            
    /* Add dark overlay */
    .main {{
        background-color: rgba(0, 0, 0, 0.65);
        padding: 20px;
        border-radius: 12px;
    }}

    /* Text color */
    h1, h2, h3, h4, h5, h6, p, span {{
        /* color: red !important; */
    }}
            
    /* Button styling */
    .stButton>button {{
        background-color: #ff4b2b;
        color: white;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }}

    .stButton>button:hover {{
        background-color: #ff6a4d;
    }}
    
    .card {{
        background: rgba(255,0,0,0.9); color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.2);
    }}
            
    div[data-testid="stLayoutWrapper"] > div:has(.card-wrapper) {{
        background: rgba(255,0,0,0.9); color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 20px;
    }}

    /* REMOVE default padding/extra wrapper */
    div[data-testid="stProgress"] > div:first-child {{
        display: none;
    }}

    /* Progress container (track) */
    div[data-testid="stProgress"] [data-baseweb="progress-bar"] {{
        
        border-radius: 12px !important;
        background-color: #2a0000 !important;
        overflow: hidden;
    }}

    /* Inner track wrapper */
    div[data-testid="stProgress"] [data-baseweb="progress-bar"] > div {{
        background-color: #2a0000 !important;
    }}

    /* Actual moving bar */
    div[data-testid="stProgress"] [role="progressbar"] > div > div {{
        background: linear-gradient(90deg, #ff0000, #ff4b2b) !important;
        border-radius: 12px !important; height: 20px !important;
    }}

    div[data-testid="stProgress"] [role="progressbar"] > div > div > div {{
        background-color: #fff !important;
    }}
    
    </style>
""", unsafe_allow_html=True)

st.title("🏁 AI Drag Race Simulator")
st.caption("Select two vehicles and simulate a quarter-mile drag race using AI.")

# Check if token exists
if not token:
    st.error("❌ GITHUB_TOKEN not found. Please check Streamlit Secrets.")
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

if "animation_played" not in st.session_state:
    st.session_state.animation_played = False

if "force_animation" not in st.session_state:
    st.session_state.force_animation = False

if "rerun_triggered" not in st.session_state:
    st.session_state.rerun_triggered = False

if "locked" not in st.session_state:
    st.session_state.locked = False

# st.write("DEBUG STATE:", {
#    "animation_played": st.session_state.animation_played,
#    "race_result": st.session_state.race_result is not None
#})

# Load Indian vehicle dataset
@st.cache_data
def load_data():
    with open("vehicles_india.json", "r", encoding="utf-8") as f:
        return json.load(f)

vehicles = load_data()

def parse_analysis_to_table(text, vehicle1, vehicle2):

    rows = []

    def extract(label):
        pattern = rf"{label}.*?(\d+\.?\d*\s*\w+).*?(\d+\.?\d*\s*\w+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2)
        return "-", "-"

    # Extract key metrics
    p1, p2 = extract("power")
    t1, t2 = extract("torque")
    a1, a2 = extract("0-60")
    b1, b2 = extract("0-100")
    q1, q2 = extract("quarter")

    rows = [
        ["Power", p1, p2],
        ["Torque", t1, t2],
        ["0-60 km/h", a1, a2],
        ["0-100 km/h", b1, b2],
        ["Quarter Mile", q1, q2],
    ]

    return rows

def extract_times(text, vehicle1, vehicle2):

    pattern1 = rf"{re.escape(vehicle1)}.*?(\d+\.?\d*)\s*(?:seconds|sec|s)"
    pattern2 = rf"{re.escape(vehicle2)}.*?(\d+\.?\d*)\s*(?:seconds|sec|s)"

    t1 = re.search(pattern1, text, re.IGNORECASE)
    t2 = re.search(pattern2, text, re.IGNORECASE)

    time1 = float(t1.group(1)) if t1 else None
    time2 = float(t2.group(1)) if t2 else None

    return time1, time2

def vehicle_selector(label):

    st.subheader(label)    

    rowcol1, row1col2 = st.columns(2)
    row2col1, row2col2 = st.columns(2)

    with rowcol1:
        v_type = st.selectbox(
            "Type",
            list(vehicles.keys()),
            key=label + "_type"
        )

    brands = list(vehicles[v_type].keys())

    with row1col2:
        brand = st.selectbox(
            "Brand",
            brands,
            key=label + "_brand"
        )

    models = list(vehicles[v_type][brand].keys())

    with row2col1:
        model = st.selectbox(
            "Model",
            models,
            key=label + "_model"
        )

    variants = vehicles[v_type][brand][model]

    with row2col2:
        variant = st.selectbox(
            "Variant",
            variants,
            key=label + "_variant"
        )

    vehicle_name = f"{brand} {model} {variant}"

    return vehicle_name

# User inputs
#left, right = st.columns([1,1])

col1, col2 = st.columns(2)

with col1:
    vehicle1 = vehicle_selector("Vehicle 1")

with col2:
    vehicle2 = vehicle_selector("Vehicle 2")

simulate = st.button("🚀 Simulate Drag Race", use_container_width=True)

def run_animation(vehicle1, vehicle2, time1, time2):

    with st.container():

        # 👇 This marker is used for CSS targeting
        st.markdown('<div class="card-wrapper"></div>', unsafe_allow_html=True)

        header_col1, header_col2 = st.columns([4, 1])

        with header_col1:
            st.markdown('<h2 class="card-title">🚦 Drag Race Animation</h2>', unsafe_allow_html=True)

        with header_col2:
            rerun = st.button("🔁 Rerun", key="rerun_anim")

        if rerun:
            st.session_state.animation_played = False
            st.session_state.force_animation = True
            st.rerun()

        st.write(vehicle1)
        bar1 = st.progress(0)

        st.write(vehicle2)
        bar2 = st.progress(0)

        should_animate = (
            not st.session_state.animation_played
            # or st.session_state.force_animation
        )

        # st.session_state.animation_played = True

        if not should_animate:
            if time1 < time2:
                bar1.progress(100)
                bar2.progress(int((time1 / time2) * 100))
            else:
                bar2.progress(100)
                bar1.progress(int((time2 / time1) * 100))
        else:
            winner_time = min(time1, time2)
            steps = 100

            for i in range(steps + 1):
                current_time = (i / steps) * winner_time

                progress1 = min(current_time / time1, 1)
                progress2 = min(current_time / time2, 1)

                bar1.progress(int(progress1 * 100))
                bar2.progress(int(progress2 * 100))

                time.sleep(0.02)

            st.session_state.animation_played = True

        if time1 < time2:
            winner = vehicle1
        elif time2 < time1:
            winner = vehicle2
        else:
            winner = "It's a Tie!"

        st.write(f"🏆 Winner: {winner}")

if simulate:

    st.session_state.animation_played = False
    st.session_state.locked = True

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

    Performance
    Power
    Torque
    Weight
    Power-to-weight ratio

    Timings
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
    time1, time2 = extract_times(result_text, vehicle1, vehicle2)
    st.session_state.time1 = time1
    st.session_state.time2 = time2
    st.session_state.vehicle1 = vehicle1
    st.session_state.vehicle2 = vehicle2 

# with right:
if st.session_state.race_result:

    # if not st.session_state.locked:
        # st.stop()        

    vehicle1 = st.session_state.vehicle1
    vehicle2 = st.session_state.vehicle2
    time1 = st.session_state.time1
    time2 = st.session_state.time2
    result_text = st.session_state.race_result       

    if time1 is None or time2 is None:
        st.warning("⚠️ Could not extract quarter-mile times from AI response.")
        st.stop() 

    st.markdown(f"""
    <div class="card">
        <h2 class="card-title">🏁 Race Result</h2>
        <h3 style="color:white; text-align:center;">
            {vehicle1} 
            <span style="margin: 10px 0; vertical-align:middle; display:block;"><img src="data:image/gif;base64,{vs_image}" alt="VS" style="max-height:75px" /></span> 
            {vehicle2}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # -----------------------------
    # RACE VISUALIZATION
    # -----------------------------

    run_animation(vehicle1, vehicle2, time1, time2)

    # -----------------------------
    # AI ANALYSIS LAST
    # -----------------------------

    st.markdown(f"""
    <div class="card">
    <h2 class="card-title">📊 AI Race Analysis</h2>    
    {result_text} 
    </div>
    """, unsafe_allow_html=True)