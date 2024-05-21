from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import PhaseType


class PhaseBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phase_type: PhaseType
    vacancy_id: int
    candidate_id: int
    interviewer_id: int
    result_link: str | None
    date: datetime

class PhaseCreateSchema(PhaseBaseSchema):
    model_config = ConfigDict(from_attributes=True)

    pass

class PhaseUpdateSchema(BaseModel):
    result_link: str
    passed: bool
    feedback: str

class PhaseCandidateCreateSchema(BaseModel):
    vacancy_id: int
    interviewer_id: int
    date: datetime

class PhaseFeedbackSendSchema(BaseModel):
    feedback:str
    feedback_send:bool = Field(default=True)

class PhaseFeedbackSendFlagSchema(BaseModel):
    feedback_send: bool
