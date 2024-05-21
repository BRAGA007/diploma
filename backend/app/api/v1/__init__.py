from app.api.v1.endpoints import (
    user,
    candidate,
    vacancy,
    phase,
)
from app.core.routes import AuthApiRouters


VERSION_PREFIX = "/v1"


routers = AuthApiRouters(prefix=VERSION_PREFIX)

for module in [
    user,
    candidate,
    vacancy,
    phase

]:
    routers.include(module.routers)

