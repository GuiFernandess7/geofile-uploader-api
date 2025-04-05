import streamlit as st
import base64

from streamlit_extras.app_logo import add_logo


def get_base64_of_bin_file(png_file):
    with open(png_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


def logo():
    add_logo("assets/transparent-logo.png", height=170)


def load_css(img, title):
    logo()
    st.markdown(
        f"""
        <style>

        .main {{
            scroll-behavior: smooth;
            background-image: url("data:image/png;base64,{img}");
        }}

        .st-emotion-cache-z5fcl4 {{
            padding-block: 0;
        }}

        .st-emotion-cache-10oheav {{
            padding: 0 1rem;
        }}

        iframe {{
            width: 100%;
        }}

        .css-1o9kxky.e1f1d6gn0 {{
            border: 2px solid #ffffff4d;
            border-radius: 4px;
            padding: 1rem;
        }}

        .css-18e3th9 {{
            padding-left: 2rem;
            padding-right: 0rem;
        }}

        .css-1d391kg {{
            padding-left: 2rem;
            padding-right: 0rem;
        }}

        .block-container {{
            padding-left: 1rem !important;
            padding-right: 0rem !important;
        }}

        [data-testid="stAppViewContainer"] > .main {{
        background-size: 180%;
        background-position: top left;
        background-repeat: no-repeat;
        background-attachment: local;
        }}

        [data-testid="stSidebar"] > div:first-child {{
        background-image: url("data:image/png;base64,{img}");
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
        }}

        [data-testid="stHeader"] {{
        background: rgba(0,0,0,0);
        }}

        [data-testid="stToolbar"] {{
        right: 2rem;
        }}

        /* Estilo para o título */
        .title {{
            font-size: 28px;
            font-family: 'Arial', sans-serif;
            color: #000000;
            position: absolute;
            top: 10px;
            left: 10px;
            margin: 0;
            z-index: 9999;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 0rem;
                padding-bottom: 0rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <h4 style="text-align: left; margin-top: 0;">
            {title}
        </h4>
        """,
        unsafe_allow_html=True,
    )


def load_all(title):
    img = get_base64_of_bin_file("assets/image2.jpg")
    load_css(img, title)
