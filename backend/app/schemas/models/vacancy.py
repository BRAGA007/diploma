import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app import settings

class VacancyBaseSchema(BaseModel):
    id:int
    title: str
    recruiter_id: int
    description: str
    specialization_list: List[str]
    head_of_department_id: int
    date_created: datetime
    date_closed: datetime | None


class VacancyCreateSchema(BaseModel):
    title: str
    recruiter_id: int = 1
    description: str
    specialization_list: List[str]
    head_of_department_id: int = 1


class VacancyUpdateSchema(BaseModel):
    title: str

    description: str
    specialization_list: List[str]
