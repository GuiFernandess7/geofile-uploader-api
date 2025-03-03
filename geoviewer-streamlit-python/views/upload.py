import streamlit as st
import requests
import time

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

URL = "http://localhost:8000/upload-kml-file"

def send_file(url, uploaded_file):
    try:
        files = {
            "file": (uploaded_file.name, uploaded_file, uploaded_file.type)
        }
        headers = {
            "Authorization": f"Bearer {st.session_state.tokenid}"
        }

        progress_bar = st.progress(0)
        status_text = st.empty()
        status_text.warning("Sending file...")

        for percent in range(0, 101, 10):
            time.sleep(0.1)
            progress_bar.progress(percent)

        response = requests.post(url, files=files, headers=headers)

        progress_bar.progress(100)
        time.sleep(0.5)

        status_text.empty()
        if response.status_code == 500:
            st.error(f"Server error: {response.content}")

        response_data = response.json()

        if response_data.get("status") == 202:
            st.success("File uploaded successfully!")
        else:
            st.error(f"Upload error: {response_data}")

    except Exception as e:
        st.error(f"Error: {str(e)}")

st.write("### Geospatial File Upload")

uploaded_file = st.file_uploader(
    "Choose a geospatial file",
    type=["kml"],
    help="Only KML File are supported",
)

if uploaded_file is not None:
    st.write("**File name:**", uploaded_file.name)
    st.write("**Type:**", uploaded_file.type)
    st.write("**Size:**", f"{uploaded_file.size / 1024:.2f} KB")

    send_button = st.button("Send File")
    if send_button:
        send_file(URL, uploaded_file)
