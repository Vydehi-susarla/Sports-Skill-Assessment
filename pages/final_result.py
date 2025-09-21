import streamlit as st

st.set_page_config(page_title="Final Results", layout="wide")

if "results" not in st.session_state or not st.session_state["results"]:
    st.error("⚠️ No results submitted yet. Please complete tests first.")
    st.stop()

results = st.session_state["results"]

st.title("🏅 Final Results Summary")

# Show results table
st.subheader("📊 Performance Summary")
rows = []
for ex, res in results.items():
    rows.append({
        "Exercise": ex,
        "Count/Reps": f"{res['count']:.2f}",
        "Accuracy (%)": f"{res['acc']:.2f}",
        "Qualified": "✅ Yes" if res['qualified'] else "❌ No"
    })

st.dataframe(rows, use_container_width=True)

# Overall Qualification
qualified_exercises = [ex for ex, r in results.items() if r['qualified']]

if len(qualified_exercises) >= 3:
    st.success("🎉 Congratulations! You are qualified for the next round!")

    st.subheader("📤 Upload Video for Sports Authority")
    
    # Sport Selection
    sport = st.selectbox(
        "Select the sport you want to register for:",
        ["Football", "Cricket", "Badminton", "Hockey", "Tennis", "Basketball"]
    )
    
    # Video Upload
    uploaded_video = st.file_uploader("Upload your sports demo video", type=["mp4", "mov", "avi"])

    if uploaded_video:
        if st.button("Submit to Sports Authority"):
            # Save to temp folder safely
            import tempfile, os
            suffix = f".{uploaded_video.name.split('.')[-1]}"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_video.read())
                video_path = tmp_file.name

            # Here you can add code to actually send video + sport info to backend or API
            # For now, just show success message
            st.success(f"✅ Video sent successfully for {sport} to the sports authority!")
            st.info(f"Saved temporarily at: {video_path}")

else:
    st.warning("⚠️ Not enough exercises qualified. Keep training and try again!")
