import logging
import re
import os

from app.domain.utils.errors import ValidationError
from app.domain.file_manager import GeoFile, GeoData
from app.domain.file_repo import FileRepository
from app.domain.user_email_repo import EmailRepository
from app.domain.geometry_repo import GeometryRepository
from app.domain.utils.errors import GCPStorageError

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


def update_database(geofile_data: GeoData, logger: logging.Logger):
    """Update database with new data"""
    email_obj = EmailRepository.insert_email(email=geofile_data.email, logger=logger)
    file_obj = FileRepository.insert_file(
        name=geofile_data.filename, email_id=email_obj.id, logger=logger
    )
    GeometryRepository.insert_geometries(
        name=geofile_data.filename,
        geometries=geofile_data.geometries,
        features=geofile_data.fields,
        file_id=file_obj.id,
        logger=logger,
    )


def start_geoprocess(message: tuple, logger: logging.Logger, env="dev"):
    """Run geoprocessing"""
    filename, email = message
    logger.info(f"[{filename}] - Email: {email}")
    validate_message(filename, logger)
    destination_filepath = f"{DESTINATION_PATH}/{filename}"

    geofile_manager = GeoFile(destination_filepath, filename, logger)

    try:
        if not geofile_manager.exists_locally():
            geofile_manager.download_from_bucket(BUCKET_NAME)
    except GCPStorageError:
        raise

    geometries, properties = extract_data_from_geofile(
        geofile_manager, logger, filename
    )
    print()
    logger.info(f"[{filename}] - Placemarks found: {len(properties)}")
    print(geometries)
    geofile_data = GeoData(
        filename=filename, email=email, geometries=geometries, fields=properties
    )
    update_database(geofile_data, logger)
    geofile_manager.delete()


# eyJlbWFpbCI6ICJ0ZXN0QGdtYWlsLmNvbSIsICJmaWxlbmFtZSI6ICJlbWJhcmdvc19pY21iaW8ua21sIn0=
# eyJlbWFpbCI6ICJ0ZXN0QGdtYWlsLmNvbSIsICJmaWxlbmFtZSI6ICJteWZpbGUua21sIn0=
# eyJmaWxlbmFtZSI6ICJzaWNhcl9pbW92ZWlzX21vY2suZ2VvanNvbiIsICJlbWFpbCI6ICJndWlsaGVybWVmczA5QGdtYWlsLmNvbSJ9
