import logging
import re
import os

from app.domain.utils.errors import ValidationError
from app.domain.file_manager import GeoFile
from app.domain.utils.errors import GCPStorageError
from app.services.firebase.auth import FirebaseClient

from dotenv import load_dotenv

load_dotenv()

ALLOWED_EXTENSIONS = "geojson"
BUCKET_NAME = os.getenv("BUCKET_NAME")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DESTINATION_PATH = os.path.join(BASE_DIR, "tmp")


def validate_message(message, logger: logging.Logger):
    """Validate PubSub message"""
    logger.info(f"[{message}] -> Validading message...")
    message_is_valid = re.match(f"^[a-zA-Z0-9_-]+\.({ALLOWED_EXTENSIONS})$", message)
    if not message_is_valid:
        logger.error(f"Message '{message}' is not valid")
        raise ValidationError(f"Message '{message}' is not valid.")


def extract_data_from_geofile(
    geofile_manager: GeoFile, logger: logging.Logger, filename: str
):
    """Extract features and geometries from geofile"""
    logger.info(f"[{filename}] - Extracting data from geofile...")
    geometries, properties = geofile_manager.extract_geometries_and_properties()
    logger.info(f"[{filename}] - Extraction Complete!")
    return geometries, properties


def update_database(collection_ref, email, filename, logger: logging.Logger):
    doc_ref = collection_ref.document(email)
    doc = doc_ref.get()

    if not doc.exists:
        logger.info(
            f"Document with email '{email}' does not exist. Creating a new document."
        )
        doc_ref.set({"data": [filename]})
        logger.info(f"New document created for email '{email}'.")
    else:
        logger.info(f"Document with email '{email}' exists.")
        doc_data = doc.to_dict()
        current_data = doc_data.get("data", [])
        current_data.append(filename)
        doc_ref.update({"data": current_data})
        logger.info(f"Item added to document for email '{email}'.")


def start_geoprocess(message: tuple, logger: logging.Logger, env="dev"):
    """Run geoprocessing"""
    filename, email = message
    logger.info(f"[{filename}] - Email FOUND")
    validate_message(filename, logger)
    destination_filepath = f"{DESTINATION_PATH}/{filename}"

    geofile_manager = GeoFile(destination_filepath, filename, logger)

    try:
        if not geofile_manager.exists_locally():
            geofile_manager.download_from_bucket(BUCKET_NAME)
    except GCPStorageError:
        raise

    firebase_client = FirebaseClient()
    database = firebase_client.get_database(name="(default)")

    collection_ref = database.collection("geofiles")
    update_database(collection_ref, email, filename, logger)
    geofile_manager.delete()


""" {
  "email": "usertest@gmail.com",
  "filename": "da39a3ee5e6b4b0d3255bfef95601890afd80709"
}
 """

# ================ MAIN PROCESSING =========================
# geometries, properties = extract_data_from_geofile(
#    geofile_manager, logger, filename
# )
# logger.info(f"[{filename}] - Placemarks found: {len(properties)}")
# geofile_data = GeoData(
#    filename=filename, email=email, geometries=geometries, fields=properties
# )
