import os

from app.domain.utils.errors import GCPStorageError
from app.services.gcp_storage import GCPStorageUploader
import shapely

import geopandas as gpd
from fiona import supported_drivers
import logging


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
        self.KMLParser = None

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
            with GCPStorageUploader(
                bucket_name=bucket_name,
                destination_path=self.filepath,
                logger=self.logger,
            ) as uploader:
                if uploader.blob_exists(self.filename):
                    self.logger.info(f"[{self.filename}] - Blob found in bucket!")
                    uploader.download_blob(self.filename)
                    self.logger.info(
                        f"[{self.filename}] - Geofile downloaded successfully!"
                    )
                else:
                    self.logger.info(f"[{self.filename}] - Blob NOT found in bucket!")
                    raise GCPStorageError(f"Blob NOT found in bucket!")
        except Exception as e:
            self.logger.error(
                f"[{self.filename}] - Error downloading file from bucket: {e}"
            )
            raise GCPStorageError(f"Error downloading file from bucket: {e}")

    def delete(self):
        self.logger.info(f"[{self.filename}] - Removing file...")
        try:
            os.remove(self.filepath)
            self.logger.info(f"[{self.filepath}] - Geofile removed successfully!")
        except Exception as e:
            self.logger.error(f"[{self.filepath}] - Error removing geofile: {e}")
            raise Exception(f"Error removing geofile: {e}")

    def extract_geometries_and_properties(self):
        supported_drivers["LIBKML"] = "rw"
        try:
            polygons = gpd.read_file(self.filepath, driver="GeoJSON")

            datetime_cols = polygons.select_dtypes(include=["datetime64[ns]"]).columns
            polygons[datetime_cols] = polygons[datetime_cols].astype(str)

            func = lambda geom: shapely.wkb.loads(
                shapely.wkb.dumps(geom, output_dimension=2)
            )
            geometries = polygons["geometry"] = (
                polygons["geometry"].apply(func).tolist()
            )
            properties = polygons.drop(columns=["geometry"]).to_dict(orient="records")

            return geometries, properties

        except Exception as e:
            self.logger.error(f"[{self.filepath}] - Error reading geofile: {e}")
            raise Exception(f"Error reading geofile: {e}")
