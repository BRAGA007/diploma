from enum import Enum
from typing import Any, Callable, Coroutine, List, Optional

from fastapi import APIRouter as FastAPIRouter
from fastapi import status
from fastapi._compat import ModelField
from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute
from pydantic._internal._model_construction import ModelMetaclass
from starlette.requests import Request
from starlette.responses import Response


class APIRouter(FastAPIRouter):
    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        include_in_schema: bool = True,
        **kwargs: Any,
    ) -> None:
        if path != "/":
            if path.endswith("/"):
                alternate_path = path[:-1]
            else:
                alternate_path = path + "/"
            super().add_api_route(alternate_path, endpoint, include_in_schema=False, **kwargs)
        return super().add_api_route(path, endpoint, include_in_schema=include_in_schema, **kwargs)


class ProxyRouter(FastAPIRouter):
    def __init__(self, *args, proxy_routers: list[FastAPIRouter], **kwargs):
        super().__init__(*args, **kwargs)
        self.proxy_routers = proxy_routers

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        include_in_schema: bool = True,
        **kwargs: Any,
    ) -> None:
        for router in self.proxy_routers:
            router.add_api_route(path, endpoint, include_in_schema=include_in_schema, **kwargs)


class AuthApiRouters:
    """
    Класс содержит в себе несколько роутеров для использования пользователями с разными привилегиями
    (неавторизованный, авторизованный, администратор)
    """

    def __init__(self, prefix: str = "", tags: list[str | Enum] | None = None):
        self.unauthorized_router = APIRouter(  # Эндпойнты,для неавторизованных
            prefix=prefix,
            tags=tags,
            route_class=ValidationSpecApiRoute,
        )
        self.tech_spec_router = APIRouter(  # Эндпойнты,для тех спецов
            prefix=prefix,
            tags=tags,
            route_class=ValidationSpecApiRoute,
        )
        self.recruiter_router = APIRouter(  # Эндпойнты, для рекрутров
            prefix=prefix,
            tags=tags,
            route_class=ValidationSpecApiRoute,
        )
        self.head_router = APIRouter(  # Эндпойнты, эндпойнты для глав отделво
            prefix=prefix,
            tags=tags,
            route_class=ValidationSpecApiRoute,
        )
        self.all_users_router = APIRouter(  # Для демонстрации на защите
            prefix=prefix,
            tags=tags,
            route_class=ValidationSpecApiRoute,
        )
        self.authorized_router = ProxyRouter(  # Эндпойнты, доступные любым авторизованным пользователям
            proxy_routers=[
                self.recruiter_router,
                self.tech_spec_router,
                self.head_router
            ],
        )

    def include(self, other: "AuthApiRouters") -> None:
        """
        Включает роутеры из другого экземпляра класса в соответствующие роутеры этого экземпляра
        :param other: другой экземпляр AuthApiRouters
        :return: None
        """
        self.tech_spec_router.include_router(other.tech_spec_router)
        self.recruiter_router.include_router(other.recruiter_router)
        self.head_router.include_router(other.head_router)
        self.all_users_router.include_router(other.all_users_router)


class ValidationSpecApiRoute(APIRoute):
    """
    Модификация стандартного APIRoute. Добавляет в схему openapi возможные ответы с ошибками валидации.
    Статус добавляемых ответов 422. Если ответ с таким статусом уже указан, в поле detail дописываются ошибки,
    которые не были указаны вручную
    """

    FIELD_PLACEHOLDERS = [
        "string",
        1,
        -1,
        100500,
        1.2,
        [],
        {},
        True,
        None,
    ]

    def __init__(self, *args, **kwargs) -> None:
        self.known_validation_errors: set[tuple[tuple, str]] = set()
        super().__init__(*args, **kwargs)

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        self.known_validation_errors = {
            (tuple(err["loc"]), err["type"])
            for err in self.responses.get(status.HTTP_422_UNPROCESSABLE_ENTITY, {})
            .get("content", {})
            .get("application/json", {})
            .get("example", {})
            .get("detail", [])
        }
        self._add_dependant_params_validation_errors(self.dependant)
        return super().get_route_handler()

    def _add_dependant_params_validation_errors(self, dependant: Dependant) -> None:
        self._add_params_validation_errors(dependant.path_params, "path")
        self._add_params_validation_errors(dependant.query_params, "query")
        self._add_params_validation_errors(dependant.header_params, "header")
        self._add_params_validation_errors(dependant.cookie_params, "cookie")
        self._add_params_validation_errors(dependant.body_params, "body")

        for dep in dependant.dependencies:
            self._add_dependant_params_validation_errors(dep)

    def _add_params_validation_errors(self, params: Optional[List[ModelField]] = None, prefix: str = "") -> None:
        if params is None:
            return

        for param in params:
            errors = []
            is_pydantic = isinstance(param.type_, ModelMetaclass)  # Проверка, что параметр - Pydantic схема
            if is_pydantic:
                errors.extend(param.validate({})[1] or [])  # Все поля пропущены

            for placeholder in self.FIELD_PLACEHOLDERS:
                errors.extend(
                    param.validate(str(placeholder))[1] or [],  # Вне pydantic моделей могут быть только строки
                )
                if is_pydantic:
                    # Если параметр - Pydantic схема, нужно провалидировать все её поля
                    fields = {key: placeholder for key in param.type_.model_fields}
                    errors.extend(param.validate(fields)[1] or [])

            for err in errors:
                if is_pydantic:
                    err["loc"] = [prefix, *err["loc"]]
                else:
                    err["loc"] = [prefix, param.name, *err["loc"]]
                # Если в кастомных валидаторах бросается исключение, оно попадает в ctx. Удаляем его
                err.pop("ctx", None)

                key = (tuple(err["loc"]), err["type"])
                if key not in self.known_validation_errors:
                    self.known_validation_errors.add(key)
                    (
                        self.responses.setdefault(status.HTTP_422_UNPROCESSABLE_ENTITY, {})
                        .setdefault("content", {})
                        .setdefault("application/json", {})
                        .setdefault("example", {})
                        .setdefault("detail", [])
                        .append(err)
                    )
