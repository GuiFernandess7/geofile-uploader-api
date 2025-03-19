import os

from app.domain.utils.errors import GCPStorageError
from app.services.gcp_storage import GCPStorageUploader

import geopandas as gpd
from fiona import supported_drivers
import logging
import xml.sax
from pprint import pprint

from app.domain.xml_parser import KMLHandler

class GeoData:
    def __init__(self, filename: str, email: str, geometries: list, fields: list):
        self.filename = filename
        self.email = email
        self.geometries = geometries
        self.fields = fields

class GeoFile:

    def __init__(self, filepath: str, filename: str, logger: logging.Logger) -> None:
        self.filepath = filepath
        self.filename = filename
        self.logger = logger
        self.handler = None
        self.parser = xml.sax.make_parser()

    def set_handler(self, handler: KMLHandler):
        self.handler = handler
        self.parser.setContentHandler(self.handler)

    def exists_locally(self) -> bool:
        self.logger.info(f"[{self.filename}] - Checking if file exists...")
        if not os.path.exists(self.filepath):
            self.logger.info(f"[{self.filename}] - Geofile does not exist in folder.")
            return False
        self.logger.info(f"[{self.filename}] - File already exists.")
        return True

    def download_from_bucket(self, bucket_name):
        self.logger.info(f"[{self.filename}] - Downloading geofile from bucket...")
        try:
            with GCPStorageUploader(bucket_name=bucket_name, destination_path=self.filepath, logger=self.logger) as uploader:
                if uploader.blob_exists(self.filename):
                    self.logger.info(f"[{self.filename}] - Blob found in bucket!")
                    uploader.download_blob(self.filename)
                    self.logger.info(f"[{self.filename}] - Geofile downloaded successfully!")
                else:
                    self.logger.info(f"[{self.filename}] - Blob NOT found in bucket!")
                    raise GCPStorageError(f"Blob NOT found in bucket!")
        except Exception as e:
            self.logger.error(f"[{self.filename}] - Error downloading file from bucket: {e}")
            raise GCPStorageError(f"Error downloading file from bucket: {e}")

    def delete(self):
        self.logger.info(f"[{self.filename}] - Removing file...")
        try:
            os.remove(self.filepath)
            self.logger.info(f"[{self.filepath}] - Geofile removed successfully!")
        except Exception as e:
            self.logger.error(f"[{self.filepath}] - Error removing geofile: {e}")
            raise Exception(f"Error removing geofile: {e}")

    def extract_geometries(self):
        supported_drivers['LIBKML'] = 'rw'
        try:
            polygons = gpd.read_file(self.filepath, driver='KML')
            return polygons["geometry"].to_list()
        except Exception as e:
            self.logger.error(f"[{self.filepath}] - Error reading geofile: {e}")
            raise Exception(f"Error reading geofile: {e}")

    def convert_to_geojson(self):
        from osgeo import gdal, ogr
        srcDS = gdal.OpenEx(self.filepath)
        filename, ext = self.filename.split('.')
        ds = gdal.VectorTranslate(filename + ".geojson", srcDS, format='GeoJSON')
        self.logger.info(f"[{self.filename}] - Converted to gejson")

    def __parse_kml(self):
        if not self.handler:
            raise ValueError("Handler is not set. Call set_handler() first.")

        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                self.parser.parse(file)
            return self.handler.placemarks
        except Exception as e:
            self.logger.error(f"[{self.filepath}] - Error parsing geofile: {e}")
            raise Exception(f"Error parsing geofile: {e}")

    def extract_fields(self):
        self.logger.info(f"[{self.filename}] - Parsing file...")
        data = self.__parse_kml()
        return data

#k = KML.parse(self.filepath)
# #fields = find_all(k, of_type=SimpleField)