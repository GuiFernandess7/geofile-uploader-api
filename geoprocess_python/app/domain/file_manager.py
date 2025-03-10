import os

from app.utils.errors import GCPStorageError
from app.services.gcp_storage import GCPStorageUploader

import geopandas as gpd
from fiona import supported_drivers
from fastkml import KML
from fastkml.utils import find_all
from fastkml import SchemaData

class GeoFile:

    def __init__(self, filepath: str, filename: str):
        self.filepath = filepath
        self.filename = filename

    def exists(self, logger) -> bool:
        logger.info(f"[{self.filename}] - Checking if file exists...")
        if not os.path.exists(self.filepath):
            logger.info(f"[{self.filename}] - Geofile does not exist in folder.")
            return False
        logger.info(f"[{self.filename}] - File already exists.")
        return True

    def download_from_bucket(self, bucket_name, logger):
        logger.info(f"[{self.filename}] - Downloading geofile from bucket...")
        try:
            with GCPStorageUploader(bucket_name=bucket_name, destination_path=self.filepath, logger=logger) as uploader:
                uploader.download_blob(self.filename)
            logger.info(f"[{self.filename}] - Geofile downloaded successfully!")
        except Exception as e:
            logger.error(f"[{self.filename}] - Error downloading file from bucket: {e}")
            raise GCPStorageError(f"Error downloading file from bucket", e)

    def delete(self, logger):
        logger.info(f"[{self.filename}] - Removing file...")
        try:
            os.remove(self.filepath)
            logger.info(f"[{self.filepath}] - Geofile removed successfully!")
        except Exception as e:
            logger.error(f"[{self.filepath}] - Error removing geofile: {e}")
            raise Exception(f"Error removing geofile: {e}")

    def extract_geometries(self, logger):
        supported_drivers['LIBKML'] = 'rw'
        try:
            polygons = gpd.read_file(self.filepath, driver='KML')
            return polygons["geometry"].to_list()
        except Exception as e:
            logger.error(f"[{self.filepath}] - Error reading geofile: {e}")
            raise Exception(f"Error reading geofile: {e}")

    def __parse(self, logger):
        try:
            k = KML.parse(self.filepath)
            schemas = find_all(k, of_type=SchemaData)
            return schemas
        except Exception as e:
            logger.error(f"[{self.filepath}] - Error parsing geofile: {e}")
            raise Exception(f"Error parsing geofile: {e}")

    def extract_fields(self, logger):
        logger.info(f"[{self.filepath}] - Parsing file...")
        schemas = self.__parse(logger)
        data_list = []
        for schema in schemas:
            if schema.data:
                logger.info(f"[{self.filepath}] - Reading schema...")
                data = {simple_data.name: simple_data.value for simple_data in schema.data}
                data_list.append(data)
        return data_list

