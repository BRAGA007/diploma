from typing import Any, Dict, Optional

from fastapi import HTTPException, status


class BaseHttpException(HTTPException):
    status_code = status.HTTP_418_IM_A_TEAPOT

    def __init__(self, detail: Any = None, headers: Optional[Dict[str, str]] = None) -> None:
        super().__init__(status_code=self.status_code, detail=detail, headers=headers)


class Http307Exception(BaseHttpException):
    status_code = status.HTTP_307_TEMPORARY_REDIRECT


class Http400Exception(BaseHttpException):
    status_code = status.HTTP_400_BAD_REQUEST


class Http401Exception(BaseHttpException):
    status_code = status.HTTP_401_UNAUTHORIZED


class Http403Exception(BaseHttpException):
    status_code = status.HTTP_403_FORBIDDEN


class Http404Exception(BaseHttpException):
    status_code = status.HTTP_404_NOT_FOUND


class Http409Exception(BaseHttpException):
    status_code = status.HTTP_409_CONFLICT


class Http422Exception(BaseHttpException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class Http523Exception(BaseHttpException):
    status_code = 523
