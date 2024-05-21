from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums import PhaseType
from app.models import User
from app.models.vacancy import Vacancy
from app.models.candidate import Candidate


class Phase(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # идентификатор вакансии
    phase_type: Mapped[PhaseType] = mapped_column(ENUM(PhaseType, inherit_schema=True), default=PhaseType.first_communication)
    vacancy_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Vacancy.id))  # идентификатор вакансии
    candidate_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Candidate.id))  # идентификатор кандидата
    interviewer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))  # идентификатор интервьюера
    result_link: Mapped[Optional[str]]  # ссылка на результаты собеседования
    feedback_send: Mapped[bool] = mapped_column(default=False)
    date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    result_link: Mapped[Optional[str]]
    passed: Mapped[Optional[bool]]
    feedback: Mapped[Optional[str]]
    interviewer: Mapped[User] = relationship("User", foreign_keys=[interviewer_id], lazy="joined")
    candidate: Mapped[Candidate] = relationship("Candidate", foreign_keys=[candidate_id],lazy="joined")
    vacancy: Mapped[Vacancy] = relationship("Vacancy", foreign_keys=[vacancy_id],lazy="joined")


