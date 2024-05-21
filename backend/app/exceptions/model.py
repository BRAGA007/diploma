from app.exceptions.http import Http404Exception
from app.schemas import ErrorModel


class ModelNotFoundError(Http404Exception):
    def __init__(self, error: ErrorModel):
        super().__init__(f"{error.class_name} [{error.value}] not found")
