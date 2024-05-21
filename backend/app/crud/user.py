import logging

from app.crud.base import CRUDBase
from app.models import User
from app.schemas.models.user import UserCreateSchema, UserUpdateSchema

logger = logging.getLogger(__name__)


class CRUDUser(CRUDBase[User, UserCreateSchema, UserUpdateSchema]):
    pass


user = CRUDUser(User)