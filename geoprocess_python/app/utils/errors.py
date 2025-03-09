class GCPStorageError(Exception):
    def __init__(self, message, errors):
        super().__init__(message)
        self.errors = errors

class ValidationError(Exception):
    def __init__(self, message):
        super().__init__(message)