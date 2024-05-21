from typing import Any

from pydantic import BaseModel

from .pulse import PulseResponseSchema


class Message(BaseModel):
    detail: str


class ErrorModel(BaseModel):
    class_name: str
    value: Any = None
