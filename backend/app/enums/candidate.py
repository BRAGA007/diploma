from __future__ import annotations

from enum import StrEnum
from functools import cache
from itertools import chain
from typing import Any


class CandidateStatus(StrEnum):
    first_communication = "первичная коммуникация"
    waiting_tech_stage = "ожидание технического собеседования"
    failed_tech_stage = "неуспешное техническое собеседование"
    success_tech_stage = "успешное техническое собеседование"
    waiting_final_stage = "ожидание финального собеседования"
    failed_final_stage = "неуспешное финальное собеседование"
    success_final_stage = "успешное финальное собеседование"
    waiting_offer = "ожидание предложения о работе"
    declined_offer = "отказ от предложения о работе"
    accepted_offer = "приглашение о работе принято"


    @classmethod
    @cache
    def items(cls) -> dict[Any, str]:
        return dict(
            chain(
                ((item.name, item) for item in cls),
                ((item.value, item) for item in cls),
            ),
        )

    @classmethod
    def get(cls, value: str) -> "CandidateStatus":
        try:
            return cls.items()[value]
        except KeyError:
            raise ValueError("Invalid input")
