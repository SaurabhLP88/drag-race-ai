import os
import streamlit as st
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get token
token = os.getenv("GITHUB_TOKEN")

st.title("🏁 AI Drag Race Simulator")
st.caption("Select two vehicles and simulate a quarter-mile drag race using AI.")

# Check if token exists
if not token:
    st.error("❌ GITHUB_TOKEN not found. Please check your .env file.")
    st.stop()

def safe_api_call(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=10)

        text = response.text.strip()

        if not text:
            st.error("API returned empty response")
            return {}

        # Handle JSONP response: callback({...})
        if text.startswith("callback"):
            start = text.find("(") + 1
            end = text.rfind(")")
            text = text[start:end]

        return json.loads(text)

    except Exception as e:
        st.error(f"API ERROR: {e}")
        return {}

@st.cache_data
def get_brands():
    url = "https://www.carqueryapi.com/api/0.3/?cmd=getMakes&callback=callback"
    data = safe_api_call(url)
    #st.write("DEBUG API RESPONSE:", data) 
    if "Makes" not in data:
        return []
    brands = [m["make_display"] for m in data["Makes"]]
    #st.write("DEBUG BRANDS:", brands[:10]) 
    return sorted(brands)

@st.cache_data
def get_models(brand):
    url = f"https://www.carqueryapi.com/api/0.3/?cmd=getModels&make={brand}&callback=callback"
    data = safe_api_call(url)

    if "Models" not in data:
        return []

    return sorted([m["model_name"] for m in data["Models"]])


@st.cache_data
def get_variants(brand, model):
    url = f"https://www.carqueryapi.com/api/0.3/?cmd=getTrims&make={brand}&model={model}&callback=callback"
    data = safe_api_call(url)

    if "Trims" not in data:
        return ["Standard"]

    variants = [
        t["model_trim"] if t["model_trim"] else "Standard"
        for t in data["Trims"]
    ]

    return list(set(variants)) if variants else ["Standard"]

def vehicle_selector(label):

    st.subheader(label)

    brands = get_brands()
    brand = st.selectbox("Brand", brands if brands else ["No brands found"], key=label+"brand")

    models = get_models(brand) if brand else []
    model = st.selectbox("Model", models if models else ["No models"], key=label+"model")

    variants = get_variants(brand, model) if model else ["Standard"]
    variant = st.selectbox("Variant", variants, key=label+"variant")

    return f"{brand} {model} {variant}"

# User inputs
col1, col2 = st.columns(2)

with col1:
    vehicle1 = vehicle_selector("Vehicle 1")

with col2:
    vehicle2 = vehicle_selector("Vehicle 2")

if st.button("Simulate Drag Race"):

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
    3. Estimate 0-100 km/h acceleration
    4. Estimate quarter mile time
    5. Predict the winner

    Output format:

    Vehicle Specs
    Vehicle 1
    Vehicle 2

    Performance
    0-100 km/h
    Quarter Mile

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

    st.success("Race Result")
    st.write(response.choices[0].message.content)