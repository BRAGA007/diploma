# import base64
#
# from fastapi import APIRouter, Request
# from fastapi.responses import RedirectResponse
#
# from app.core.config import settings
# from app.exceptions.http import Http401Exception
#
#
# router = APIRouter()
#
# MAX_AGE = 3600 * 24 * 14
#
#
# @router.get("/")
# async def oidc_callback(request: Request, state: str, code: str) -> RedirectResponse:
#     """Эндпойнт для получения редиректа с ISSO"""
#     state_value, encoded_path = state.split(".")
#     if not request.app.auth.check_state(state_value):
#         raise Http401Exception(detail="Incorrect state")
#
#     path = base64.urlsafe_b64decode(encoded_path.encode("utf-8")).decode("utf-8")
#     admin_ui = path.startswith("https://admin.")
#     session_id = await request.app.auth.create_session(code, admin_ui)
#     response = RedirectResponse(path)
#     response.set_cookie(settings.session_cokkie_name, session_id, max_age=MAX_AGE)
#
#     return response
