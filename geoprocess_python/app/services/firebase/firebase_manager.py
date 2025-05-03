import firebase_admin
from firebase_admin import credentials
from google.cloud import secretmanager
import os
import json
import logging


class FirebaseServiceManager:

    def __init__(
        self, local: bool = False, project_id: str = None, secret_id: str = None
    ):
        self.logger = logging.getLogger(__name__)
        self.local = local
        self.project_id = project_id
        self.secret_id = secret_id
        self.CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.CREDENTIALS_FIREBASE_PATH = os.path.join(
            self.CURRENT_DIR, ".creds/firebase.json"
        )
        self.app = None

    def init_firebase(self):
        if firebase_admin._apps:
            self.app = firebase_admin.get_app()
            self.logger.info("Firebase app already initialized.")
            return self.app

        if self.local:
            cred = credentials.Certificate(self.CREDENTIALS_FIREBASE_PATH)
            self.logger.info("[LOCAL] -> Firebase app STARTING...")
        else:
            try:
                client = secretmanager.SecretManagerServiceClient()
                secret = f"projects/{self.project_id}/secrets/{self.secret_id}/versions/latest"
                response = client.access_secret_version(name=secret)
                firebase_config = json.loads(response.payload.data.decode("UTF-8"))
                cred = credentials.Certificate(firebase_config)
                self.logger.info("[GCP] -> Firebase app STARTING...")
            except Exception as e:
                self.logger.error(f"Error accessing secret: {str(e)}")
                raise ValueError(f"Error accessing secret: {str(e)}")

        try:
            self.app = firebase_admin.initialize_app(cred)
            self.logger.info(f"Firebase app initialized with project ID: {self.app.project_id}")
            return self.app
        except Exception as e:
            self.logger.error(f"Error initializing firebase: {str(e)}")
            raise ValueError(f"Error initializing firebase: {str(e)}")

    def get_client(self, name):
        try:
            self.init_firebase()
            from google.cloud import firestore

            self.logger.info("[SUCCESS] -> Database up and running.")
            return firestore.Client(project=self.app.project_id, database=name)
        except Exception as e:
            raise ValueError(f"Error initializing database: {str(e)}")
