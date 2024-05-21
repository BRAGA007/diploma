import logging

from app.core.config import settings
from app.exceptions import http, model


logging.basicConfig(format="%(asctime)s %(levelname)s: %(name)s: %(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(settings.logging_level)
