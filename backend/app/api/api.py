from typing import Any

from fastapi import APIRouter, Depends, status

from app.api import v1
# from app.auth import AuthRequired



UNAUTHORIZED_RESPONSES: dict[int | str, dict[str, Any]] = {
    status.HTTP_401_UNAUTHORIZED: {
        "content": {
            "application/json": {
                "example": {"detail": "Unauthorized"},
            },
        },
    },
}

unauthorized_router = APIRouter()  # Эндпойнты, доступные без авторизации

all_users_router = APIRouter(
    prefix="/api",
    responses=UNAUTHORIZED_RESPONSES,
)  # Эндпойнты, доступные в пользовательском API
head_router = APIRouter(
    prefix="/head_api",
    responses=UNAUTHORIZED_RESPONSES,
)  # Эндпойнты, доступные в админском API


for prefix in ["/api", "/head_api"]:
    unauthorized_router.include_router(v1.routers.unauthorized_router, prefix=prefix)

all_users_router.include_router(v1.routers.all_users_router)

head_router.include_router(v1.routers.head_router)



api_router = APIRouter()
api_router.include_router(unauthorized_router)
api_router.include_router(all_users_router)
api_router.include_router(head_router)
