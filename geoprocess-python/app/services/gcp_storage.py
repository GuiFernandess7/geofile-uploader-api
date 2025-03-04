import logging
from google.cloud import storage

class GCPStorageUploader:
    def __init__(self, bucket_name, destination_path, logger: logging.Logger):
        self.bucket_name = bucket_name
        self.destination_path = destination_path
        self.logger = logger
        self.storage_client = storage.Client()

    def __enter__(self):
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.logger.info(f"Connected to bucket: {self.bucket_name}")
        return self

    def download_blob(self, source_blob_name):
        """Download geofile from bucket"""
        blob = self.bucket.blob(source_blob_name)
        blob.download_to_filename(self.destination_path)

        self.logger.info(
            f"Downloaded storage object {source_blob_name} from bucket {self.bucket_name} to local file {self.destination_path}."
        )

    def __exit__(self, exc_type, exc_value, traceback):
        self.logger.info(f"Exiting context for bucket: {self.bucket_name}")
        if exc_type:
            self.logger.error(f"Exception encountered: {exc_value}")
        return False
