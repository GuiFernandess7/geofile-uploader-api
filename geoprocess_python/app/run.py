import logging
import re
import os

from google.cloud import storage
from fiona.drvsupport import supported_drivers
import geopandas as gpd

from app.utils.errors import GCPStorageError, ValidationError
from app.services.gcp_storage import GCPStorageUploader

from dotenv import load_dotenv
load_dotenv()

ALLOWED_EXTENSIONS="kml"
BUCKET_NAME = os.getenv("BUCKET_NAME")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DESTINATION_PATH = os.path.join(BASE_DIR, "tmp")

def validate_message(message, logger: logging.Logger):
    """Validate PubSub message"""
    message_is_valid = re.match(f"^[a-zA-Z0-9_-]+\.({ALLOWED_EXTENSIONS})$", message)
    if not message_is_valid:
        logger.error(f"Message '{message}' is not valid")
        raise ValidationError(f"Message '{message}' is not valid.")

def file_exists(filepath):
    return os.path.exists(filepath)

def download_geofile(filename, destination_filepath, logger):
    logger.info(f"[{filename}] - Downloading geofile from bucket...")
    try:
        with GCPStorageUploader(bucket_name=BUCKET_NAME, destination_path=destination_filepath, logger=logger) as uploader:
            uploader.download_blob(filename)
    except Exception as e:
        logger.error(f"[{filename}] - Error downloading file from bucket: {e}")
        raise GCPStorageError(f"Error downloading file from bucket", e)

def remove_geofile(filepath, logger):
    try:
        os.remove(filepath)
    except Exception as e:
        logger.error(f"[{filepath}] - Error removing geofile: {e}")
        raise Exception(f"Error removing geofile: {e}")

def process_geofile(filepath):
    supported_drivers['LIBKML'] = 'rw'
    polygons = gpd.read_file(filepath, driver='KML')
    return polygons

def start_geoprocessing(message_str, logger: logging.Logger, env='dev'):
    """Run geoprocessing"""
    logger.info(f"[{message_str}] -> Validading message...")
    validate_message(message_str, logger)
    filename = message_str
    destination_filepath = f"{DESTINATION_PATH}/{filename}"

    logger.info(f"[{message_str}] - Checking if file exists...")
    if not file_exists(destination_filepath):
        download_geofile(filename, destination_filepath, logger)
    else:
        logger.info(f"[{filename}] - File already exists")

    logger.info(f"[{filename}] - Processing geofile...")
    polygons = process_geofile(destination_filepath)
    logger.info(f"[{filename}] - Processing Complete!")

    polygons.boundary.plot()

    logger.info(f"[{filename}] - Removing file...")
    remove_geofile(destination_filepath, logger)
    logger.info(f"[{filename}] - File removed successfully.")
