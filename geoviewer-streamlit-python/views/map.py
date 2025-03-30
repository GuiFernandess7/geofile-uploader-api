import streamlit as st
import leafmap.foliumap as leafmap
from services.postgis import PostGISConnection, PostGISHandler
import os
from styles.custom import load_all

load_all(title="Map View")

if "current_map" not in st.session_state:
    st.session_state.current_map = ""

try:
    conn = PostGISConnection(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )
except Exception as e:
    st.error("Database connection failed.")
    raise Exception(f"Database connection error: {e}")

db_manager = PostGISHandler(connection=conn)
if db_manager.engine is None:
    st.stop()
else:
    df = db_manager.execute_query(
        f"""
            SELECT name FROM files
            WHERE email_id IN (SELECT id FROM emails WHERE email = '{st.session_state.user_email}');
            """
    )
    col1, col2 = st.columns([4, 1])

    if df.empty:
        map_options = []
    else:
        files = df["name"].to_list()
        map_options = [file for file in files if file]

    with col2:
        st.session_state.current_map = st.sidebar.selectbox(
            "Map options", map_options, index=0 if map_options else None
        )

    apply_button = st.sidebar.button("Apply")

    with col1:
        if apply_button:
            query = f"""
                SELECT geometry, features
                FROM geometries
                WHERE file_id IN (SELECT id FROM files WHERE name = '{st.session_state.current_map}');
            """

            gdf = db_manager.execute_query(query, geom_col="geometry")
            m = leafmap.Map(
                locate_control=True,
                latlon_control=True,
                draw_export=True,
                minimap_control=True,
            )
            m.add_basemap()
            m.add_gdf(gdf)
            m.to_streamlit(height=400, width=600)
        else:
            st.success("Choose a terrain on the side bar.")
