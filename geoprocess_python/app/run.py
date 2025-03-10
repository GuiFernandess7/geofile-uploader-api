import logging
import re
import os

from app.utils.errors import ValidationError
from app.domain.file_manager import GeoFile

from dotenv import load_dotenv
load_dotenv()

ALLOWED_EXTENSIONS="kml"
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

def start_geoprocessing(message_str, logger: logging.Logger, env='dev'):
    """Run geoprocessing"""
    validate_message(message_str, logger)
    filename = message_str
    destination_filepath = f"{DESTINATION_PATH}/{filename}"

    geofile_manager = GeoFile(destination_filepath, filename)
    if not geofile_manager.exists(logger):
        geofile_manager.download_from_bucket(filename, destination_filepath, logger)

    logger.info(f"[{filename}] - Processing geofile...")
    geometries = geofile_manager.extract_geometries(logger)
    fields = geofile_manager.extract_fields(logger)
    logger.info(f"[{filename}] - Processing Complete!")

    logger.info(f"[{filename}] - Geometries found: {len(geometries)}")
    if len(geometries) != len(fields):
        raise ValueError("Number of geometries different from number of fields.")

    #geofile_manager.delete(logger)
