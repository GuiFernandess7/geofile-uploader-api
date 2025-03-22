import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "tokenid" not in st.session_state:
    st.session_state["tokenid"] = ""


def logout():
    st.session_state["tokenid"] = ""
    st.session_state.logged_in = False
    st.rerun()


logout_page = st.Page(logout, title="Log out", icon=":material/logout:")
login_page = st.Page("views/auth.py", title="Log out", icon=":material/logout:")

map_dashboard = st.Page(
    "views/map.py", title="Map", icon=":material/map:", default=False
)

upload_dashboard = st.Page(
    "views/upload.py", title="KML", icon=":material/folder:", default=True
)

if st.session_state.logged_in:
    pg = st.navigation(
        {
            "Account 👤": [logout_page],
            "Upload 📑": [upload_dashboard],
            "Dashboard 🌍": [map_dashboard],
        }
    )
else:
    pg = st.navigation(
        {
            "Account": [login_page],
            "Map": [],
        }
    )

pg.run()
