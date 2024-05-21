from typing import Optional

from sqlalchemy.ext.hybrid import hybrid_property

from app.db.base import Base
from sqlalchemy import BigInteger,SQLColumnExpression
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from app.enums import UserType


class User(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str]  # имя
    last_name: Mapped[str]  # фамилия
    middle_name: Mapped[Optional[str]]  # Опционально, так как отчество может отсутствовать
    email: Mapped[str]
    user_type: Mapped[UserType] = mapped_column(ENUM(UserType, inherit_schema=True))

    @hybrid_property
    def display_name(self) -> str:
        """ Метод для отображения имени в формате Фамилия Имя"""
        return f"{self.last_name} {self.first_name}"


    @display_name.inplace.expression
    @classmethod
    def _display_name_expression(cls) -> SQLColumnExpression[str]:
        return User.last_name + " " + User.first_name
