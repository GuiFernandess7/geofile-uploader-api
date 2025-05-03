import firebase_admin
from firebase_admin import credentials
from google.cloud import secretmanager
import os
import json
import logging

logger = logging.getLogger(__name__)


class FirebaseServiceManager:

    def __init__(
        self, local: bool = False, project_id: str = None, secret_id: str = None
    ):
        self.local = local
        self.project_id = project_id
        self.secret_id = secret_id
        self.CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        self.CREDENTIALS_FIREBASE_PATH = os.path.join(
            self.CURRENT_DIR, ".creds/service_account.json"
        )
        self.app = None

    def init_firebase(self):
        if firebase_admin._apps:
            self.app = firebase_admin.get_app()
            return self.app

        if self.local:
            cred = credentials.Certificate(self.CREDENTIALS_FIREBASE_PATH)
        else:
            client = secretmanager.SecretManagerServiceClient()
            secret = (
                f"projects/{self.project_id}/secrets/{self.secret_id}/versions/latest"
            )
            response = client.access_secret_version(name=secret)
            firebase_config = json.loads(response.payload.data.decode("UTF-8"))
            cred = credentials.Certificate(firebase_config)

        self.app = firebase_admin.initialize_app(cred)
        return self.app

    def get_database(self, name):
        try:
            self.init_firebase()
            from google.cloud import firestore

            return firestore.Client(project=self.app.project_id, database=name)
        except Exception as e:
            raise ValueError(f"Error initializing firebase: {str(e)}")
