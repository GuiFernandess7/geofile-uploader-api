class GCPStorageError(Exception):
    def __init__(self, message):
        super().__init__(message)

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)