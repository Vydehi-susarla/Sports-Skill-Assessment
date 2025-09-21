import streamlit as st

st.set_page_config(page_title="Home", page_icon="🏠")

st.title("Welcome to Sports Talent Identification Portal 🏅")

st.write("""
Our project gives **equal chances** for all athletes, even from small towns or villages.

👉 To get started, please login or sign up.
""")

# Sidebar
with st.sidebar:
    if "logged_in" in st.session_state and st.session_state.logged_in:
        st.write(f"👤 Logged in as **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.switch_page("home.py")
    else:
        if st.button("Login / Signup"):
            st.switch_page("pages/app.py")
