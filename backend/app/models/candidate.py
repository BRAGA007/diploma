from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.enums import CandidateStatus


class Candidate(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # уникальный идентификатор
    status: Mapped[CandidateStatus] = mapped_column(ENUM(CandidateStatus, inherit_schema=True), default=CandidateStatus.first_communication)
    first_name: Mapped[str]  # имя
    last_name: Mapped[str]  # фамилия
    middle_name: Mapped[Optional[str]]  # Опционально, так как отчество может отсутствовать
    telegram: Mapped[str]  # телеграм аккаунт
    resume_link: Mapped[str]  # ссылка на резюме
    date_created: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # дата первой коммуникации

    @hybrid_property
    def display_name(self) -> str:
        """ Метод для отображения имени в формате Фамилия Имя"""
        return f"{self.last_name} {self.first_name}"
