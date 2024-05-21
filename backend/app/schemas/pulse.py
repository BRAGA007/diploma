from datetime import datetime

from pydantic import BaseModel, Field, field_serializer
from pydantic_core.core_schema import SerializationInfo


class PulseResponseSchema(BaseModel):
    """Схема ответа на эндпойнт pulse"""

    db_connection: bool
    current_datetime: datetime = Field(examples=[datetime.now().strftime("%Y.%m.%d %H:%M:%S")])

    @field_serializer("current_datetime")
    def serialize_datetime(self, current_datetime: datetime, _info: SerializationInfo) -> str:
        return current_datetime.strftime("%Y.%m.%d %H:%M:%S")
