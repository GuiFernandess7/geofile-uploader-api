from .firebase_manager import FirebaseServiceManager
import os


class FirebaseClient:

    def __init__(self):
        self.firebase_manager: FirebaseServiceManager = FirebaseServiceManager(
            local=os.getenv("FIREBASE_LOCAL", "false").lower() == "true",
            project_id=os.getenv("FIREBASE_PROJECT_ID"),
            secret_id=os.getenv("FIREBASE_SECRET_ID"),
        )

    def get_database(self, name):
        return self.firebase_manager.get_client(name)
