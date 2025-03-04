import logging
import re
import os

from google.cloud import storage

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

def start_geoprocessing(message_str, logger: logging.Logger, env='dev'):
    """Run geoprocessing"""
    logger.info(f"[{message_str}] -> Validading message...")
    validate_message(message_str, logger)
    filename = message_str
    logger.info(f"[{message_str}] - Downloading geofile from bucket...")
    destination_filepath = f"{DESTINATION_PATH}/{filename}"

    logger.info(f"[{message_str}] - Checking if file exists...")
    # TODO: Check if file exists

    try:
        with GCPStorageUploader(BUCKET_NAME, DESTINATION_PATH, logger) as uploader:
            uploader.download_blob(destination_filepath)
    except Exception as e:
        logger.error(f"[{message_str}] - Error downloading file from bucket: {e}")
        raise GCPStorageError(f"Error downloading file from bucket", e)

    logger.info(f"[{filename}] - File downloaded successfully!")

    logger.info(f"[{filename}] - Processing geofile...")
    # TODO: File processing
    logger.info(f"[{filename}] - Processing Complete!")

    logger.info(f"[{filename}] - Removing file...")
    os.remove(destination_filepath)




