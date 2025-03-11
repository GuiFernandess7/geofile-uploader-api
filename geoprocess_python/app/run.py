import logging
import re
import os

from app.domain.utils.errors import ValidationError
from app.domain.file_manager import GeoFile
from app.domain.xml_parser import KMLHandler
from app.domain.file_repo import FileRepository

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

def extract_data_from_geofile(geofile_manager: GeoFile, logger: logging.Logger, filename: str):
    logger.info(f"[{filename}] - Processing geofile...")
    geometries = geofile_manager.extract_geometries()
    fields = geofile_manager.extract_fields()
    logger.info(f"[{filename}] - Processing Complete!")
    return fields, geometries

def start_geoprocess(message_str, logger: logging.Logger, env='dev'):
    """Run geoprocessing"""
    validate_message(message_str, logger)
    filename = message_str
    destination_filepath = f"{DESTINATION_PATH}/{filename}"

    geofile_manager = GeoFile(destination_filepath, filename, logger)
    geofile_manager.set_handler(handler=KMLHandler())
    if not geofile_manager.exists():
        geofile_manager.download_from_bucket(BUCKET_NAME)

    fields, geometries = extract_data_from_geofile(geofile_manager, logger, destination_filepath)
    logger.info(f"[{filename}] - Placemarks found: {len(fields)}")

    FileRepository.insert_file(name=filename)

    #geofile_manager.delete(logger)
