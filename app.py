import asyncio
from copilot import CopilotClient
import streamlit as st
import json
import re
import time
import base64

def get_base64_image(image_path):
    with open(image_path, "rb") as img:
        return base64.b64encode(img.read()).decode()

# Convert images to base64
try:
    bg_image = get_base64_image("images/sunshine-01.jpg")
    vs_image = get_base64_image("images/versus-01.png")

except FileNotFoundError as e:
    st.error(f"Required image file not found: {e.filename}")
    st.stop()

except OSError as e:
    st.error(f"Could not read an image file: {e}")
    st.stop()

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

    [data-testid="stHeading"] h1 {{
        font-size:3.2rem; font-weight: 900;
    }}

    @media (max-width: 767.98px) {{
        [data-testid="stHeading"] h1 {{
            font-size:2.2rem;
        }}
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

    .card-body {{
        color:white; text-align:center; font-size: 2.4rem; font-weight: 900;
    }}

    .card table th,
    .card table td {{
        padding: 5px;
    }}

    @media (max-width: 1199.98px) {{
        .card-body {{
            font-size: 1rem;
        }}
    }}

    .vs-style {{margin: 10px 0; vertical-align:middle; display:inline-block; }}

    @media (max-width: 767.98px) {{
        .vs-style {{
            display: block;
        }}
    }}
    
    .vs-style img {{ max-height:75px }}
            
    div[data-testid="stLayoutWrapper"] > div:has(.card-wrapper) {{
        background: rgba(255,0,0,0.9); color: white;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.2);
        margin-bottom: 20px;
    }}

    /*div[data-testid="stLayoutWrapper"] > .stHorizontalBlock > .stColumn {{
        min-width: initial !important;
    }}*/

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

    
    /* ==================================
    VEHICLE SELECTOR PARENT CONTAINERS
    ================================== */

    .st-key-vehicle-1-card,
    .st-key-vehicle-2-card {{
        width: 100%;
        min-width: 0;
        box-sizing: border-box;
        /*padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        border-radius: 12px;
        background: rgba(249, 189, 101, 0.5);*/
    }}

    /* Child row containers */
    .st-key-vehicle-1-row-one,
    .st-key-vehicle-1-row-two,
    .st-key-vehicle-2-row-one,
    .st-key-vehicle-2-row-two {{
        width: 100%;
        min-width: 0;
    }}

    /* Ensure each selectbox fills its column */
    .st-key-vehicle-1-card [data-testid="stSelectbox"],
    .st-key-vehicle-2-card [data-testid="stSelectbox"] {{
        width: 100%;
        min-width: 0;
    }}

    /* Keep column contents from overflowing */
    .st-key-vehicle-1-card [data-testid="stColumn"],
    .st-key-vehicle-2-card [data-testid="stColumn"] {{
        min-width: 0;
    }}

    /* ==================================
    TABLET
    ================================== */

    @media (max-width: 900px) {{
        .st-key-vehicle-1-card,
        .st-key-vehicle-2-card {{
            padding: 15px;
        }}
    }}

    /* ==================================
    MOBILE
    ================================== */

    @media (max-width: 600px) {{
        .st-key-vehicle-1-card,
        .st-key-vehicle-2-card {{
            padding: 12px;
        }}

        .st-key-vehicle-1-row-one [data-testid="stHorizontalBlock"],
        .st-key-vehicle-1-row-two [data-testid="stHorizontalBlock"],
        .st-key-vehicle-2-row-one [data-testid="stHorizontalBlock"],
        .st-key-vehicle-2-row-two [data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap;
            gap: 0.5rem;
        }}

        .st-key-vehicle-1-row-one [data-testid="stColumn"],
        .st-key-vehicle-1-row-two [data-testid="stColumn"],
        .st-key-vehicle-2-row-one [data-testid="stColumn"],
        .st-key-vehicle-2-row-two [data-testid="stColumn"] {{
            flex: 1 1 100%;
            width: 100%;
        }}
    }}

    /* Outer two-vehicle layout */
    .st-key-vehicle-comparison-layout {{
        width: 100%;
        min-width: 0;
    }}

    .st-key-vehicle-comparison-layout [data-testid="stColumn"] {{
        min-width: 0;
    }}

    @media (max-width: 600px) {{
        .st-key-vehicle-comparison-layout [data-testid="stHorizontalBlock"] {{
            flex-wrap: wrap;
        }}

        .st-key-vehicle-comparison-layout [data-testid="stColumn"] {{
            flex: 1 1 100%;
            width: 100%;
        }}
    }}

    
    </style>
""", unsafe_allow_html=True)

st.title("🏁 Virtual Drag Race")
st.caption("Select two vehicles and simulate a quarter-mile drag race using AI.")

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

try:
    vehicles = load_data()

    if not isinstance(vehicles, dict) or not vehicles:
        st.error("Vehicle data must be a non-empty JSON object.")
        st.stop()

except FileNotFoundError:
    st.error(
        "vehicles_india.json was not found. "
        "Place it in the project directory."
    )
    st.stop()

except json.JSONDecodeError as e:
    st.error(f"Invalid JSON in vehicles_india.json: {e}")
    st.stop()

except OSError as e:
    st.error(f"Could not read vehicle data: {e}")
    st.stop()


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


async def _ask_copilot_async(prompt: str) -> str:
    client = CopilotClient()

    try:
        await client.start()

        session = await client.create_session(model="auto")

        response = await session.send_and_wait(prompt)
        result = response.data.content

        if not isinstance(result, str) or not result.strip():
            raise RuntimeError(
                "GitHub Copilot returned an empty response."
            )

        return result.strip()

    finally:
        await client.stop()


def ask_copilot(prompt: str) -> str:
    return asyncio.run(_ask_copilot_async(prompt))


def vehicle_selector(label):
    with st.container(key=f"{label.lower().replace(' ', '-')}-card"):
        st.subheader(label)

        # Parent container for the first row
        with st.container(key=f"{label.lower().replace(' ', '-')}-row-one"):
            rowcol1, rowcol2 = st.columns(2)

            with rowcol1:
                v_type = st.selectbox(
                    "Type",
                    list(vehicles.keys()),
                    key=label + "_type"
                )

            brands = list(vehicles[v_type].keys())

            with rowcol2:
                brand = st.selectbox(
                    "Brand",
                    brands,
                    key=label + "_brand"
                )

        # Parent container for the second row
        with st.container(key=f"{label.lower().replace(' ', '-')}-row-two"):
            row2col1, row2col2 = st.columns(2)

            with row2col1:
                models = list(vehicles[v_type][brand].keys())

                model = st.selectbox(
                    "Model",
                    models,
                    key=label + "_model"
                )

            with row2col2:
                variants = vehicles[v_type][brand][model]

                variant = st.selectbox(
                    "Variant",
                    variants,
                    key=label + "_variant"
                )

    return f"{brand} {model} {variant}"


# User inputs
#left, right = st.columns([1,1])

with st.container(key="vehicle-comparison-layout"):
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
        
    prompt = f"""
    You are **Virtual Drag Race 🏁**, an expert automotive performance analyst
    and drag-racing commentator.

    Analyze a hypothetical **quarter-mile drag race (402.3 metres)**
    between the following vehicles:

    - 🏎️ **Vehicle 1:** {vehicle1}
    - 🏎️ **Vehicle 2:** {vehicle2}

    ## 🎯 YOUR OBJECTIVES

    1. Estimate engine power, torque, and kerb weight.
    2. Estimate 0–60 km/h and 0–100 km/h acceleration times.
    3. Calculate power-to-weight ratio.
    4. Estimate quarter-mile elapsed time.
    5. Compare the vehicles and declare a winner.
    6. Explain the result using technical reasoning.

    ## 📋 OUTPUT FORMAT

    Follow the Markdown structure below exactly. Use readable tables,
    bold highlights, and relevant emojis. Do not output HTML.

    🏁 Virtual Drag Race — DRAG RACE REPORT

    ### 🚘 Race Line-up
    | Specification | Vehicle 1 | Vehicle 2 |
    |---|---|---|
    | **Vehicle** | {vehicle1} | {vehicle2} |

    ### ⚙️ 1. Performance Specifications

    | 📊 Metric | 🏎️ {vehicle1} | 🏎️ {vehicle2} |
    |---|---:|---:|
    | Power | XX.X bhp | XX.X bhp |
    | Torque | XX.X Nm | XX.X Nm |
    | Kerb Weight | XXXX kg | XXXX kg |
    | Power-to-Weight | XX.X bhp/tonne | XX.X bhp/tonne |

    ### ⏱️ 2. Acceleration & Drag Times

    | 🏁 Test | 🏎️ {vehicle1} | 🏎️ {vehicle2} |
    |---|---:|---:|
    | 0–60 km/h | X.X seconds | X.X seconds |
    | 0–100 km/h | X.X seconds | X.X seconds |
    | Quarter Mile (402.3 m) | XX.X seconds | XX.X seconds |

    For every timing, lower is better. Clearly distinguish estimated
    times from verified manufacturer figures.

    ### 🏆 3. Race Verdict

    **🥇 Winner:** [Exact winning vehicle name]

    **⏱️ Winning quarter-mile time:** XX.X seconds

    **📏 Estimated winning margin:** X.X seconds

    ### 🔍 4. Why Did It Win?

    Explain the result in 3–5 concise bullet points. Discuss power,
    torque, weight, power-to-weight ratio, traction, gearing, and
    acceleration where relevant. Do not claim to know exact launch
    conditions or traction data unless supplied.

    ### 📈 5. Performance Breakdown

    Briefly compare:
    - 💪 **Power:** Which vehicle has the advantage?
    - ⚖️ **Weight:** Which vehicle is lighter?
    - 🚀 **Acceleration:** Which vehicle is quicker off the line?
    - 🏁 **Quarter mile:** Which vehicle reaches the finish first?

    ### ⚠️ 6. Accuracy & Assumptions

    State which figures are estimates and identify important missing
    data, such as exact variant specifications, transmission, tyres,
    traction, and test conditions.

    ## 📌 ACCURACY RULES

    - Use the exact vehicle names supplied above throughout the report.
    - Never invent specifications and present them as verified facts.
    - Prefer reliable, variant-specific specifications when known.
    - If reliable data is unavailable, provide a clearly labelled estimate
    or state "Data unavailable".
    - Keep units consistent: bhp, Nm, kg, bhp/tonne, km/h, seconds.
    - Calculate power-to-weight as bhp divided by weight in tonnes.
    - Make the winner consistent with the estimated quarter-mile times.
    - If the difference is negligible or uncertain, explain that the
    result could change under real-world conditions.
    - Always provide a numerical quarter-mile time in seconds for BOTH
    vehicles so the simulator can extract their times.
    - Do not claim that a simulated result is a real-world test result.

    Make the report exciting, professional, technically useful,
    and easy to read.

    ### 🤖 MACHINE-READABLE RACE DATA

    RACE_TIME_1: {vehicle1} - XX.X seconds 
    RACE_TIME_2: {vehicle2} - XX.X seconds

    """    
    
    try:
        with st.spinner("Simulating drag race... 🏁"):
            result_text = ask_copilot(prompt)

    except Exception as e:
        st.error("Could not generate the race analysis with GitHub Copilot.")
        st.code(f"{type(e).__name__}: {e}")
        st.stop()

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
        st.warning(
            "Could not extract both quarter-mile times. "
            "The AI analysis is still available below."
        )
    else:
        st.markdown(f"""
        <div class="card">
            <h2 class="card-title">🏁 Race Result</h2>
            <div class="card-body">
                {vehicle1} 
                <span class="vs-style"><img src="data:image/gif;base64,{vs_image}" alt="VS" /></span> 
                {vehicle2}
            </div>
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