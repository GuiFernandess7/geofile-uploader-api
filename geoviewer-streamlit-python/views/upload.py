import streamlit as st

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

st.title("KML File Upload")

uploaded_file = st.file_uploader(
    "Choose a KML File",
    type=["kml"],
    help="Only KML files are supported.",
)

if uploaded_file is not None:
    st.success("KML File loaded successfully!")
    st.write("**File name:**", uploaded_file.name)
    st.write("**File type:**", uploaded_file.type)
    st.write("**File size:**", f"{uploaded_file.size / 1024:.2f} KB")

    st.download_button(
        label="Download KML",
        data=uploaded_file,
        file_name=uploaded_file.name,
        mime="application/vnd.google-earth.kml+xml",
    )
else:
    st.info("Please, upload file before continuing.")
