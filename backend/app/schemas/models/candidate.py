from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import CandidateStatus, PhaseType


class CandidateBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    status: CandidateStatus
    first_name: str
    last_name: str
    middle_name: str
    telegram: str
    resume_link: str

class CandidateCreateSchema(CandidateBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    pass


class CandidateUpdateSchema(CandidateBaseSchema):
    pass

class CandidateListSchema(CandidateBaseSchema):
    id: int


class CandidateAndPhaseCreateSchema(CandidateCreateSchema):
    model_config = ConfigDict(from_attributes=True)
    phase_type: PhaseType
    interviewer_id: int =1
    result_link: str | None
    date: datetime | None
