"""Эндпойнт для работы с сущностью пользователей
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.routes import AuthApiRouters
from app.crud import user
from app.enums import UserType
from app.models import User

routers = AuthApiRouters(prefix="/users", tags=["users"])


@routers.all_users_router.get(
    "/get_tech_spec",
)
async def get_tech_spec(db: AsyncSession = Depends(get_db)):
    """Выводит всех технических специалистов"""
    tech_spec = await user.list(
        db, clauses=[User.user_type == UserType.technical_specialist]
    )
    return tech_spec
