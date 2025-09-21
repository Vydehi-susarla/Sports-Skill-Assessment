import streamlit as st
import json, os, hashlib, binascii

st.set_page_config(page_title="Login / Signup", page_icon="🔑")

USERS_FILE = "users.json"

# Helpers...
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password, salt=None):
    if salt is None:
        salt_bytes = os.urandom(16)
    else:
        salt_bytes = binascii.unhexlify(salt) if isinstance(salt, str) else salt
    pwd_hash = hashlib.pbkdf2_hmac("sha256", password.encode(), salt_bytes, 100_000)
    return binascii.hexlify(salt_bytes).decode(), binascii.hexlify(pwd_hash).decode()

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

users = load_users()

st.title("Login / Signup")

with st.sidebar:
    if st.session_state.logged_in:
        st.write(f"👤 Logged in as **{st.session_state.username}**")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.switch_page("home.py")

col1, col2 = st.columns(2)

# Login form
with col1:
    st.header("Login")
    with st.form("login_form"):
        login_user = st.text_input("Username")
        login_pass = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
    if submitted:
        if login_user in users:
            salt = users[login_user]["salt"]
            _, hash_try = hash_password(login_pass, salt)
            if hash_try == users[login_user]["password"]:
                st.success("Login successful ✅")
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.switch_page("pages/tests.py")
            else:
                st.error("Incorrect password.")
        else:
            st.error("User not found. Please sign up.")

# Signup form
with col2:
    st.header("Sign up")
    with st.form("signup_form"):
        new_user = st.text_input("Choose a username")
        new_pass = st.text_input("Choose a password", type="password")
        sign_sub = st.form_submit_button("Create account")
    if sign_sub:
        if not new_user or not new_pass:
            st.error("Please enter both username and password.")
        elif new_user in users:
            st.error("Username already exists.")
        else:
            salt_hex, pwd_hash_hex = hash_password(new_pass)
            users[new_user] = {"salt": salt_hex, "password": pwd_hash_hex}
            save_users(users)
            st.success("Account created ✅ Now login on the left.")
