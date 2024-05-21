import logging

from app.crud.base import CRUDBase
from app.models import Phase
from app.schemas.models import PhaseCreateSchema, PhaseUpdateSchema

logger = logging.getLogger(__name__)


class CRUDPhase(CRUDBase[Phase, PhaseCreateSchema, PhaseUpdateSchema]):
    pass


phase = CRUDPhase(Phase)