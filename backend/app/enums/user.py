from __future__ import annotations

from enum import StrEnum


class UserType(StrEnum):
    """Типы пользователей информационной системы"""

    recruiter = "Рекрутер"
    head_of_department = "Руководитель отдела"
    technical_specialist = "Технический специалист"

   # @classmethod
 #   def get(cls, value: str) -> "UserType":
     #   try:
      #      return cls(value)
       # except ValueError:
         #   return cls.UserType

