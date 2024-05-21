from datetime import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.user import User


class Vacancy(Base):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Идентификатор вакансии
    title: Mapped[str]  # название
    recruiter_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))  # идентификатор рекрутера
    description: Mapped[str]  # описание
    specialization_list: Mapped[List[str]] = mapped_column(ARRAY(String))  # список компетенций
    head_of_department_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(User.id))  # идентификатор руководителя
    date_created: Mapped[datetime] = mapped_column(default=datetime.utcnow)  # дата создания
    date_closed: Mapped[Optional[datetime]]  # дата закрытия
    recruiter: Mapped[User] = relationship("User", foreign_keys=[recruiter_id], lazy="joined")
    head_of_department: Mapped[User] = relationship("User", foreign_keys=[head_of_department_id],lazy="joined")
