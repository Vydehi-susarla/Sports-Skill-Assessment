import streamlit as st
import os, joblib
import pandas as pd
import numpy as np
import cv2

# --- Page Config ---
st.set_page_config(page_title="Sports Talent Evaluation Portal", layout="wide")

# --- Sidebar Logout ---
if "logged_in" in st.session_state and st.session_state.logged_in:
    with st.sidebar:
        st.write(f"👤 Logged in as **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.switch_page("home.py")
else:
    st.error("You must login first to access this page.")
    st.stop()

st.title("Sports Talent Evaluation Portal 🏆")
st.success(f"Welcome {st.session_state.username} 👋 You can now attempt the tests.")

# ==============================
# Paths and Model Loading
# ==============================
MODEL_DIR = "models"
try:
    reg = joblib.load(os.path.join(MODEL_DIR, "regressor_model.joblib"))
    scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.joblib"))
    feature_cols = joblib.load(os.path.join(MODEL_DIR, "feature_cols.joblib"))
    models_loaded = True
except Exception as e:
    reg, scaler, feature_cols = None, None, None
    models_loaded = False
    load_error = str(e)

# ==============================
# Ideal Ranges and Min Counts
# ==============================
ideal_ranges = {
    "Running": {"Rate_per_sec": (1.0, 3.0), "Efficiency": (0.01, 0.10), "Frames_per_sec": (22, 40), "Energy_index": (25, 110)},
    "Push-ups": {"Rate_per_sec": (0.6, 2.0), "Efficiency": (0.01, 0.05), "Frames_per_sec": (15, 30), "Energy_index": (12, 45)},
    "Sit-ups": {"Rate_per_sec": (0.5, 1.5), "Efficiency": (0.008, 0.04), "Frames_per_sec": (12, 28), "Energy_index": (10, 35)},
    "Long Jumps": {"Rate_per_sec": (0.3, 1.0), "Efficiency": (0.01, 0.04), "Frames_per_sec": (12, 22), "Energy_index": (8, 30)},
    "Vertical Jump": {"Rate_per_sec": (0.3, 1.2), "Efficiency": (0.01, 0.05), "Frames_per_sec": (12, 25), "Energy_index": (8, 35)}
}
min_counts = {"Running": 12, "Push-ups": 10, "Sit-ups": 10, "Long Jumps": 5, "Vertical Jump": 5}

# ==============================
# Video Handling
# ==============================
def extract_features(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    if frame_count <= 0: frame_count = 1
    if fps <= 0: fps = 30

    duration = frame_count / (fps + 1e-5)
    count_or_height = max(1, frame_count // int(fps + 1e-5))

    features = {
        "Start_Frame": 0,
        "End_Frame": frame_count,
        "Duration": duration,
        "Time_Taken": duration,
        "FPS": fps,
        "Count_or_Height": count_or_height,
        "Rate_per_sec": count_or_height / (duration + 1e-5),
        "Frames_per_sec": frame_count / (duration + 1e-5),
        "Energy_index": fps * (count_or_height / (duration + 1e-5)),
        "Efficiency": count_or_height / (frame_count + 1e-5),
        "Speed_index": duration / (fps + 1e-5),
        "Explosiveness": (count_or_height**2) / (duration * fps + 1e-5)
    }
    cap.release()
    return pd.DataFrame([features])

def compute_form_accuracy(features, ex_type):
    if ex_type not in ideal_ranges:
        return 0
    scores = []
    for feat, (low, high) in ideal_ranges[ex_type].items():
        val = features.iloc[0][feat]
        if low <= val <= high:
            scores.append(1.0)
        else:
            diff = max(low - val, val - high)
            tolerance = high - low
            penalty = min(1.0, diff / (tolerance + 1e-5))
            scores.append(max(0.0, 1.0 - penalty))
    return np.mean(scores) * 100

def predict_from_video(video_path, ex_type):
    features = extract_features(video_path)
    X_input = features.reindex(columns=feature_cols, fill_value=0)
    X_scaled = scaler.transform(X_input)
    reg_pred = reg.predict(X_scaled)
    count = float(reg_pred[0])
    acc = compute_form_accuracy(features, ex_type)
    qualified = (acc >= 50) and (count >= min_counts.get(ex_type, 0))
    return count, acc, qualified, features

# ==============================
# Page Layout
# ==============================
st.markdown("<h1 style='text-align: center; color: #2E86C1;'>🏆 Sports Analysis Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

if not models_loaded:
    st.error(f"❌ Models could not be loaded. Error: {load_error}")
    st.stop()

exercise_options = ["Running", "Push-ups", "Sit-ups", "Vertical Jump", "Long Jumps"]

for ex_type in exercise_options:
    st.subheader(f"⚡ {ex_type}")
    uploaded_file = st.file_uploader(
        f"Upload a video for {ex_type}",
        type=["mp4", "mov", "avi"],
        key=f"file_{ex_type}"
    )

    import tempfile

    if uploaded_file:
    # Create a temp file safely
        suffix = f".{uploaded_file.name.split('.')[-1]}"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name  # path to use for processing

    # Prediction button
        if st.button(f"Predict {ex_type}", key=f"predict_{ex_type}"):
            with st.spinner("Processing video..."):
                try:
                    count, acc, qualified, features = predict_from_video(video_path, ex_type)

                    st.metric("Qualified?", "✅ Yes" if qualified else "❌ No")

                    st.session_state[f"result_{ex_type}"] = {
                    "count": count,
                    "acc": acc,
                    "qualified": qualified,
                    "features": features,
                    "video_path": video_path
                }

                except Exception as e:
                    st.error(f"Error: {str(e)}")


    # 🔑 Always show "See Full Results" if prediction was already done
    if f"result_{ex_type}" in st.session_state:
        if st.button(f"See Full Results for {ex_type}", key=f"see_{ex_type}"):
            st.session_state["selected_exercise"] = ex_type
            st.switch_page("pages/exercise_result.py")


# ==============================
# Final Submission
# ==============================
if st.button("Submit All Results"):
    st.session_state["results"] = {
        ex: {
            "count": st.session_state[f"result_{ex}"]["count"],
            "acc": st.session_state[f"result_{ex}"]["acc"],
            "qualified": st.session_state[f"result_{ex}"]["qualified"]
        }
        for ex in exercise_options
        if f"result_{ex}" in st.session_state
    }
    st.session_state["submitted"] = True
    st.success("✅ All test results have been submitted!")
    st.switch_page("pages/final_result.py")
