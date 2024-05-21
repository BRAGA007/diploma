# import logging
# from typing import Any, Iterable, NoReturn
#
# from fastapi import Request
#
# from app.core.config import settings
# from app.exceptions.http import Http401Exception, Http403Exception
#
#
# logger = logging.getLogger(__name__)
#
#
# class AuthRequired:
#     def __init__(self, roles: Iterable[str]):
#         self.roles = frozenset(roles)
#
#     async def get_scope(self, request: Request) -> dict:
#         logger.debug(f"Checking roles: {', '.join(self.roles)}")
#         session_id = request.cookies.get(settings.session_cokkie_name, None)
#         if not session_id:
#             redirect_to_auth(request)
#         try:
#             token_info = await request.app.auth.get_token(session_id)
#         except Http401Exception:
#             token_info = None
#         if token_info is None:
#             redirect_to_auth(request)
#
#         resource = token_info["resource_access"].get(settings.keycloak_client_id)
#         user_roles = resource["roles"] if resource else []
#         return {
#             "username": token_info.get("preferred_username", ""),
#             "full_name": token_info.get("fullname", ""),
#             "first_name": token_info.get("given_name", ""),
#             "middle_name": token_info.get("middle_name", ""),
#             "last_name": token_info.get("family_name", ""),
#             "employee_id": token_info.get("employeeID", ""),
#             "email": token_info.get("email", ""),
#             "roles": user_roles,
#             "photo": settings.hrgate_photo + token_info.get("preferred_username", ""),
#         }
#
#     async def __call__(self, request: Request):
#         user_scope = await self.get_scope(request)
#         request.scope["user"] = user_scope
#         if self.roles.difference(user_scope["roles"]):  # Если нет каких-то из требуемых ролей
#             raise Http403Exception()
#
#     def __hash__(self):
#         return hash(self.roles)
#
#     def __eq__(self, other: Any):
#         if isinstance(other, AuthRequired):
#             return self.roles == other.roles
#         return False
#
#
# def redirect_to_auth(request: Request) -> NoReturn:
#     path = request.headers.get("referer", request.url.path)
#     if request.url.query:
#         path += "?" + request.url.query
#     redirect_url = request.app.auth.get_auth_url(path)
#     raise Http401Exception(headers={"auth_url": redirect_url})
