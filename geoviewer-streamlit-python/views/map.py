import streamlit as st
import leafmap.foliumap as leafmap
from shapely import wkt
import geopandas as gpd
import pandas as pd

if "current_map" not in st.session_state:
    st.session_state.current_map = ""

logo = "https://i.imgur.com/UbOXYAU.png"
st.sidebar.image(logo, width=120)

st.write("#### Demo Map View")

conn = st.connection("postgresql", type="sql")

df = conn.query(
    """
    SELECT name FROM files
    WHERE email_id IN (SELECT id FROM emails WHERE email = :email);
    """,
    params={"email": st.session_state.get("user_email", "")},
    ttl="10m",
)

col1, col2 = st.columns([4, 1])

if df.empty:
    map_options = []
else:
    files = df["name"].to_list()
    map_options = [file.split(".")[0] for file in files if file]

with col2:
    st.session_state.current_map = st.sidebar.selectbox(
        "Map options", map_options, index=0 if map_options else None
    )

if st.session_state.current_map:
    geodata = conn.query(
        """
        SELECT ST_AsText(geometry) AS geometry, features
        FROM geometries
        WHERE file_id IN (SELECT id FROM files WHERE name LIKE :current_map || '%');
        """,
        params={"current_map": st.session_state.current_map},
        ttl="10m",
    )
    geodata["geometry"] = geodata["geometry"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(geodata, geometry="geometry")
else:
    gdf = None

apply_button = st.sidebar.button("Apply")

with col1:
    if apply_button and gdf is not None:
        # geojson = leafmap.gdf_to_geojson(gdf, epsg="4326")
        m = leafmap.Map(
            locate_control=True,
            latlon_control=True,
            draw_export=True,
            minimap_control=True,
        )
        m.add_basemap()
        m.add_gdf(gdf)
        m.to_streamlit(height=700)
        # st.dataframe(gdf)
