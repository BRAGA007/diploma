from __future__ import annotations

from enum import StrEnum


class PhaseType(StrEnum):
    """Виды собеседований"""

    first_communication = "Первичная коммуникация"
    technical_interview = "техническое собеседование"
    final_interview = "финальное интервью"