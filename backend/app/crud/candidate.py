import logging

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.crud.base import CRUDBase
from app.enums import CandidateStatus

from app.models import Candidate
from app.schemas.models.candidate import CandidateCreateSchema, CandidateUpdateSchema

logger = logging.getLogger(__name__)


class CRUDCandidate(CRUDBase[Candidate, CandidateCreateSchema, CandidateUpdateSchema]):
    async def _change_status(self, db: AsyncSession, candidate_id: int, status: CandidateStatus) -> None:
        """Изменение статуса кандидата"""
        query = update(self._table).values(status=status).where(self._table.id == candidate_id)
        await db.execute(query)
        await db.commit()

    async def set_waiting_tech_stage_status(self, db: AsyncSession, candidate_id: int) -> None:
        """Назначено техническое интервью"""
        await self._change_status(db, candidate_id, CandidateStatus.waiting_tech_stage)

    async def set_waiting_final_stage_status(self, db: AsyncSession, candidate_id: int) -> None:
        """Назначено финальное интервью"""
        await self._change_status(db, candidate_id, CandidateStatus.waiting_final_stage)

    async def set_failed_tech_stage_status(self, db: AsyncSession, candidate_id: int) -> None:
        """Техническое интервью не пройдено"""
        await self._change_status(db, candidate_id, CandidateStatus.failed_tech_stage)

    async def set_success_tech_stage_status(self, db: AsyncSession, candidate_id: int) -> None:
        """Техническое интервью пройдено"""
        await self._change_status(db, candidate_id, CandidateStatus.success_tech_stage)

    async def set_success_final_stage_status(self, db: AsyncSession, candidate_id: int) -> None:
        """Финальное интервью не пройдено"""
        await self._change_status(db, candidate_id, CandidateStatus.success_final_stage)

    async def set_failed_final_stage_status(self, db: AsyncSession, candidate_id: int) -> None:
        """Финальное интервью не пройдено"""
        await self._change_status(db, candidate_id, CandidateStatus.failed_final_stage)

    waiting_offer = "ожидание предложения о работа"
    declined_offer = "отказ от предложения о работе"
    accepted_offer = "приглашение о работе принято"

    async def set_waiting_offer_status(self, db: AsyncSession, candidate_id: int) -> None:
        """Отправлена обратная связь с оффером"""
        await self._change_status(db, candidate_id, CandidateStatus.waiting_offer)

    async def set_declined_offer_status(self, db: AsyncSession, candidate_id: int) -> None:
        """Откзалася от оффера"""
        await self._change_status(db, candidate_id, CandidateStatus.declined_offer)

    async def set_accepted_offer_status(self, db: AsyncSession, candidate_id: int) -> None:
        """Принл оффер"""
        await self._change_status(db, candidate_id, CandidateStatus.accepted_offer)


candidate = CRUDCandidate(Candidate)