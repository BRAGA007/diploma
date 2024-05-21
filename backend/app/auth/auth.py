# import base64
# import logging
# import random
# import string
# from datetime import datetime
# from typing import Dict, Set
#
# import keycloak
#
# import app.db.session
# from app.core.config import settings
#
# from app.exceptions.http import Http401Exception
#
#
#
# logger = logging.getLogger(__name__)
#
#
# class KeyCloakConnector:  # наверное, стоит оформить как singleton
#     def __init__(self):
#         self.kc = keycloak.KeycloakOpenID(
#             server_url=settings.keycloak_server_url,
#             client_id=settings.keycloak_client_id,
#             realm_name=settings.keycloak_realm_name,
#             client_secret_key=settings.keycloak_client_secret,
#         )
#         self.kc_public_key = "-----BEGIN PUBLIC KEY-----\n" + self.kc.public_key() + "\n-----END PUBLIC KEY-----"
#         self.options = {"verify_signature": True, "verify_aud": False, "verify_exp": True}
#         self.grant_type = "authorization_code"
#
#     def decode_token(self, token: str) -> dict:
#         try:
#             token_info = self.kc.decode_token(token, key=self.kc_public_key, options=self.options)
#         except Exception as err:
#             raise Http401Exception() from err
#         return token_info
#
#     def token(self, code: str, admin_ui: bool = False) -> dict:
#         redirect_uri = settings.keycloak_admin_redirect_uri if admin_ui else settings.keycloak_redirect_uri
#         try:
#             tokens = self.kc.token(grant_type=self.grant_type, code=code, redirect_uri=redirect_uri)
#         except Exception as e:
#             raise Http401Exception(detail="Unable to get access token.") from e
#         return tokens
#
#     def refresh_token(self, refresh_token: str) -> dict:
#         try:
#             tokens = self.kc.refresh_token(refresh_token)
#         except keycloak.exceptions.KeycloakPostError as e:
#             raise Http401Exception(detail="Session not active") from e
#         return tokens
#
#     def introspect_token(self, token: str) -> dict:
#         token_info = self.kc.introspect(token)
#         return token_info
#
#     def auth_url(self, path: str, state: str, admin_ui: bool = False) -> str:
#         redirect_uri = settings.keycloak_admin_redirect_uri if admin_ui else settings.keycloak_redirect_uri
#         auth_url = self.kc.auth_url(
#             redirect_uri=redirect_uri,
#             scope=settings.keycloak_scope,
#             state=f"{state}.{path}",
#         )
#         return auth_url
#
#
# class Session:
#     def __init__(self, code: str, admin_ui: bool = False):
#         current_time = int(datetime.now().timestamp())
#         self.connector = KeyCloakConnector()
#         tokens = self.connector.token(code, admin_ui)
#         self.session_id = tokens["session_state"]
#         self.access_token = tokens["access_token"]
#         self.access_token_payload = self.connector.decode_token(self.access_token)
#         self.refresh_token = tokens["refresh_token"]
#         self.last_introspection = current_time
#         self.access_exp = current_time + int(tokens["expires_in"])
#         self.refresh_exp = current_time + int(tokens["refresh_expires_in"])
#
#     def get_session_id(self) -> str:
#         return self.session_id
#
#     def get_token_info(self) -> dict:
#         return self.connector.decode_token(self.access_token)
#
#     async def refresh(self) -> None:
#         current_time = int(datetime.now().timestamp())
#         tokens = self.connector.refresh_token(self.refresh_token)
#         self.access_token = tokens["access_token"]
#         self.access_token_payload = self.connector.decode_token(self.access_token)
#         self.refresh_token = tokens["refresh_token"]
#         self.last_introspection = current_time
#         self.access_exp = current_time + int(tokens["expires_in"])
#         self.refresh_exp = current_time + int(tokens["refresh_expires_in"])
#
#         await self.add_account_or_last_login()
#
#     def _introspect_token(self) -> bool:
#         token_info = self.connector.introspect_token(self.access_token)
#         if token_info == {"active": False}:
#             return False
#         logger.debug(f"Introspecting token from session {self.session_id}")
#         self.last_introspection = int(datetime.now().timestamp())
#         return True
#
#     async def validate(self) -> bool:
#         current_time = int(datetime.now().timestamp())
#         if current_time >= self.access_exp:
#             if current_time >= self.refresh_exp:
#                 logger.debug("Session expired")
#                 return False
#             else:
#                 logger.debug("Access token expired, using refresh token to get new one.")
#                 await self.refresh()
#         else:
#             if self.last_introspection + settings.keycloak_introspection_delay <= current_time:
#                 return self._introspect_token()
#         return True
#
#     def logout(self) -> None:
#         self.connector.kc.logout(self.refresh_token)
#
#
# class Auth:
#     states: Set[str] = set()
#     sessions: Dict[str, Session] = {}
#
#     def _generate_state(self, length: int = 32) -> str:
#         state = "".join(random.SystemRandom().choice(string.ascii_lowercase + string.digits) for _ in range(length))
#         if state in self.states:
#             return self._generate_state(length)
#         self.states.add(state)
#         return state
#
#     async def _validate_session(self, session_id: str) -> bool:
#         session = self.sessions.get(session_id)
#         if not session:
#             logger.debug("Session not found")
#             return False
#         return await session.validate()
#
#     def check_state(self, state: str) -> bool:
#         if state not in self.states:
#             return False
#         self.states.remove(state)
#         return True
#
#     async def create_session(self, code: str, admin_ui: bool = False) -> str:
#         logger.debug("Getting access token")
#         new_session = Session(code, admin_ui)
#         session_id = new_session.get_session_id()
#         self.sessions[session_id] = new_session
#         return session_id
#
#     async def refresh_session(self, session_id: str) -> None:
#         session = self.sessions[session_id]
#         await session.refresh()
#
#     async def get_token(self, session_id: str) -> dict | None:
#         if not (await self._validate_session(session_id)):
#             logger.debug("Session validation error")
#             return None
#         session = self.sessions.get(session_id)
#         if not session:
#             logger.debug("Session not found")
#             return None
#         return session.get_token_info()
#
#     def get_auth_url(self, redirect_to: str) -> str:
#         path = base64.urlsafe_b64encode(redirect_to.encode("utf-8")).decode("utf-8")
#         admin_ui = redirect_to.startswith("https://admin.")
#         auth_url = KeyCloakConnector().auth_url(path, self._generate_state(), admin_ui)
#         return auth_url
