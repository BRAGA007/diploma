import re
from typing import Any, ClassVar

from sqlalchemy import MetaData, Table
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase

from app import settings


class Base(AsyncAttrs, DeclarativeBase):
    convention = {
        "table_schema": lambda _, table: table.schema,
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_schema)s_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_schema)s_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_schema)s_%(table_name)s_%(column_0_name)s__%"
        "(referred_table_name)s_%(referred_column_0_name)s",
        "pk": "pk_%(table_schema)s_%(table_name)s",
    }

    id: Any
    metadata = MetaData(schema=settings.postgres_schema, naming_convention=convention)  # type: ignore # noqa
    __table__: ClassVar[Table]

    # Генерируем названия таблиц автоматически из названия модели преобразуя PascalCase в snake_case
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return re.sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()
