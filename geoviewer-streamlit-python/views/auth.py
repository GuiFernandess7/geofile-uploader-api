import streamlit as st
import requests
import os
import re
from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv

st.set_page_config(
    page_title="Authentication",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
        .stTabs [data-baseweb="tab-list"] button {
            color: green !important;
        }

        .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
            border-bottom: 2px solid green !important;
            color: green !important;
        }

        .stButton>button {
            background-color: green !important;
            color: white !important;
            border-radius: 8px;
            border: none;
        }

        .stButton>button:hover {
            background-color: darkgreen !important;
        }

        .stTextInput>div>div>input {
            border: 2px solid green !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

load_dotenv()

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")
TARGET_URL = os.getenv("TARGET_URL")

if "tokenid" not in st.session_state:
    st.session_state["tokenid"] = ""
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

def validate_email_input(email):
    try:
        valid = validate_email(email)
        return valid.email
    except EmailNotValidError as e:
        st.error("Invalid email.")
        return None

def validate_password_input(password):
    if not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
        st.error("Password must be at least 8 characters long, including letters and numbers.")
        return False
    return True

def sign_up(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }

        response = requests.post(url, json=data)
        response_data = response.json()

        if "idToken" in response_data:
            id_token = response_data["idToken"]
            st.session_state["tokenid"] = id_token
            st.success("User registered successfully!")
            return id_token
        else:
            st.error(f"Sign-up error: {response_data.get('error', {}).get('message', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

def authenticate(email, password):
    try:
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"

        data = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }

        response = requests.post(url, json=data)
        response_data = response.json()

        if "idToken" in response_data:
            id_token = response_data["idToken"]
            st.session_state["tokenid"] = id_token
            st.session_state.logged_in = True
            st.success("Login successfull!")
            return id_token
        else:
            st.error(f"Login error: {response_data.get('error', {}).get('message', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

col1, col2 = st.columns([1, 1])

with col2:
    st.markdown(
        """
        <style>
        .vertical-center {
            display: flex;
            justify-content: right;
            align-items: center;
        }
        </style>
        <div class="vertical-center">
        """,
        unsafe_allow_html=True,
    )

    st.image("assets/logo2.png", width=470)
    st.markdown("</div>", unsafe_allow_html=True)

with col1:
    tab1, tab2 = st.tabs(["Sign Up", "Login"])

    with tab1:
        st.header("Sign Up")
        email_signup = st.text_input("Enter your email (Sign-Up)")
        password_signup = st.text_input("Enter your password (Sign-Up)", type="password")

        if st.button("Register"):
            if email_signup and password_signup:
                email_signup = validate_email_input(email_signup)
                st.success("Registration successful!")
                if email_signup and validate_password_input(password_signup):
                    id_token = sign_up(email_signup, password_signup)
                    if id_token:
                        st.rerun()

    with tab2:
        st.header("Login")
        email_login = st.text_input("Enter your email (Login)")
        password_login = st.text_input("Enter your password (Login)", type="password")

        if st.button("Login"):
            if email_login and password_login:
                email_login = validate_email_input(email_login)
                if email_login:
                    id_token = authenticate(email_login, password_login)
                    if id_token:
                        st.success("Login successful!")
                        st.rerun()
