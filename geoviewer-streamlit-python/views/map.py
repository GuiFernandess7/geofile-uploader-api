import streamlit as st
import folium
from streamlit_folium import st_folium
import os
from styles.custom import load_all
import hashlib
from services.firebase import FirebaseServiceManager
from google.cloud import storage
import geojson
import rasterio
from rasterio.plot import reshape_as_image
import numpy as np
import matplotlib.pyplot as plt
from folium.raster_layers import ImageOverlay

load_all(title="Map Viewer")


def hash_email(email: str) -> str:
    h = hashlib.sha1()
    h.update(email.encode("utf-8"))
    return h.hexdigest()


if "current_map" not in st.session_state:
    st.session_state.current_map = ""

if "terrain_loaded" not in st.session_state:
    st.session_state.terrain_loaded = False

if "terrains" not in st.session_state:
    db_manager = FirebaseServiceManager(local=True)
    db_manager.init_firebase()
    db = db_manager.get_database("(default)")

    email_hash = hash_email(st.session_state.user_email)
    terrains = db.collection("geofiles").document(email_hash).get().to_dict()["data"]

    st.session_state.terrains = terrains
else:
    terrains = st.session_state.terrains

if "gcs_client" not in st.session_state or "gcs_bucket" not in st.session_state:
    client = storage.Client()
    bucket_name = "geokml-bucket"
    bucket = client.get_bucket(bucket_name)

    st.session_state.gcs_client = client
    st.session_state.gcs_bucket = bucket
else:
    client = st.session_state.gcs_client
    bucket = st.session_state.gcs_bucket

selected_terrain = st.sidebar.selectbox("Select a terrain", terrains)
local_tiff_path = os.path.join(os.getcwd(), "tmp/ndvi_image_02.tiff")

if st.sidebar.button("Load terrain and NDVI"):
    st.session_state.terrain_loaded = True

if st.session_state.terrain_loaded:
    blob = bucket.blob(selected_terrain)

    geojson_data = blob.download_as_text()
    terrain_data = geojson.loads(geojson_data)

    coords = terrain_data["features"][0]["geometry"]["coordinates"][0]
    center_lat = sum(c[1] for c in coords) / len(coords)
    center_lon = sum(c[0] for c in coords) / len(coords)

    m = folium.Map(
        location=[center_lat, center_lon],
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        attr="Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
    )

    folium.GeoJson(terrain_data, name="Terreno").add_to(m)

    if os.path.exists(local_tiff_path):
        with rasterio.open(local_tiff_path) as src:
            bounds = src.bounds  # Obtendo os limites do raster (bounding box)
            image = src.read(
                1
            )  # Lendo o primeiro canal da imagem (assumindo uma imagem 1-banda)

            # Normalizando a imagem (caso necessário)
            norm_image = (image - image.min()) / (image.max() - image.min())

            # Aplicando a colormap
            colormap = plt.cm.RdYlGn
            colored_image = np.uint8(
                colormap(norm_image) * 255
            )  # Convertendo para uma imagem RGB

            # Reshape da imagem para o formato adequado para o folium (3 canais de cores RGB)
            colored_image = reshape_as_image(colored_image)[
                :, :, :3
            ]  # Remover o canal alfa, se houver

            image_overlay = ImageOverlay(
                image=colored_image,
                bounds=[[bounds.bottom, bounds.left], [bounds.top, bounds.right]],
                opacity=1,
                name="NDVI",
            )
            image_overlay.add_to(m)
    else:
        st.warning(f"Arquivo TIFF não encontrado em: {local_tiff_path}")

    with st.form(key="map-form"):
        st_folium(m, width=800, height=500, returned_objects=[])
        st.form_submit_button("Save Map", on_click=None)
