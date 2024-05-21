import logging

from app.crud.base import CRUDBase
from app.models import Vacancy
from app.schemas.models.vacancy import VacancyCreateSchema, VacancyUpdateSchema

logger = logging.getLogger(__name__)


class CRUDVacancy(CRUDBase[Vacancy, VacancyCreateSchema, VacancyUpdateSchema]):
    pass


vacancy = CRUDVacancy(Vacancy)