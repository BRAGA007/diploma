import uuid
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app import settings

class UserBaseSchema(BaseModel):
    """Общие поля"""

    display_name: str = Field(examples=["Иванов Иван"])
    first_name: str = Field(examples=["Иван"])
    middle_name: str = Field(examples=["Иванович"])
    last_name: str = Field(examples=["Иванов"])
    is_active: Optional[bool] = True


class UserCreateSchema(UserBaseSchema):
    """Поля возвращаемые при создании объекта User"""

#
# class UserHrGateCreateSchema(UserCreateSchema):
#     hrgate_id: Optional[uuid.UUID] = Field(examples=["d7bcca8e-a5fd-4bd3-8e66-8d7d54d9bd79"])
#     photo: str = Field(examples=[settings.hrgate_photo])
#
#
class UserUpdateSchema(UserBaseSchema):
    """Поля получаемы при обновлении записи пользователя"""

#
# class UserInDBBase(UserBaseSchema):
#     """Общие поля для моделей хранящихся в БД"""
#
#     model_config = ConfigDict(from_attributes=True)
#
#     id: int = Field(examples=[1])
#
#
# class UserSchema(UserInDBBase):
#     """Поля возвращаемые при просмотре конкретной записи"""
#
#     photo: str | None = Field(examples=[settings.hrgate_photo + "iiivanov"])
#
#
# class TeamRoleSchema(BaseModel):
#     """Поля возвращаемые при просмотре списка ролей члена команды"""
#
#     model_config = ConfigDict(from_attributes=True)
#
#     id: int = Field(examples=[1])
#     title: str = Field(examples=["Product Owner"])
#
#
# class UserRoleSchema(UserSchema):
#     """Схема служит для отображения пользователя с ролями, которые он занимает в команде"""
#
#
# class CurrentUserTeamSchema(BaseModel):
#     id: int = Field(examples=[1])
#     product_id: int = Field(examples=[1])
#     title: str = Field(examples=["DataOps Portal"])
#     team_key: str = Field(examples=["DOP"])
#     permissions: list[TeamPermission] = Field(default_factory=list)
#     roles: List[str] = Field(examples=[["dev", "devops"]], default_factory=list)
#
#
# class CurrentUserProductSchema(BaseModel):
#     id: int = Field(examples=[1])
#     title: str = Field(examples=["DataOps"])
#     product_key: str = Field(examples=["DOP"])
#     permissions: list[ProductPermission] = Field(default_factory=list)
#     roles: List[ProductRole] = Field(examples=[["po", "cpo"]], default_factory=list)
#     status: ProductStatus = Field(examples=["active"])
#
#
# class CurrentUserSchema(BaseModel):
#     id: int | None = Field(examples=[1], default=None)
#     username: str = Field(examples=["iivanov"])
#     full_name: str = Field(examples=["Иванов Иван Иванович"])
#     first_name: str = Field(examples=["Иван"])
#     middle_name: str = Field(examples=["Иванович"])
#     last_name: str = Field(examples=["Иванов"])
#     employee_id: str = Field(examples=["123456"])
#     roles: list[str] = Field(examples=[["admin"]])
#     has_pending_applications: bool = Field(default=False)
#     email: str = Field(examples=["iivanov@mts.ru"])
#     photo: str | None = Field(examples=[settings.hrgate_photo + "iivanov"])
#     permissions: list[PortalPermission] = Field(default_factory=list)
#     products: List[CurrentUserProductSchema] = Field(default_factory=list)
#     teams: List[CurrentUserTeamSchema] = Field(default_factory=list)
#
#
# class UserDetailSchema(BaseModel):
#     """Поля возвращаемые при просмотре детальной информации о конкретном пользователе"""
#
#     model_config = ConfigDict(from_attributes=True)
#
#     id: int = Field(examples=[1])
#     display_name: str = Field(examples=["Иванов Иван"])
#     photo: str | None = Field(examples=[settings.hrgate_photo + "iivanov"])
#     is_active: bool
#     accounts: List[AccountForUserSchema]
#
#
# class OwnerSchema(BaseModel):
#     """Поля возвращаемые при выводе списка владельцев команды или продукта"""
#
#     model_config = ConfigDict(from_attributes=True)
#
#     id: int = Field(examples=[1])
#     display_name: str = Field(examples=["Иванов Иван"])
