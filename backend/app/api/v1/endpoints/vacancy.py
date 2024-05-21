"""Эндпойнт для работы с сущностью пользователей
"""

import telebot
from fastapi import Depends, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.api.deps import get_db, db
from app.core.routes import AuthApiRouters
from app.crud import user, vacancy, candidate, phase
from app.enums import UserType, CandidateStatus, PhaseType
from sqlalchemy.orm import aliased
from app.models import User, Vacancy
from app.schemas.models import (
    CandidateCreateSchema,
    CandidateAndPhaseCreateSchema,
    PhaseCreateSchema,
)
from app.schemas.models.vacancy import VacancyCreateSchema, VacancyUpdateSchema

templates = Jinja2Templates(directory="app/templates")
routers = AuthApiRouters(prefix="/vacancies", tags=["vacancies"])


@routers.all_users_router.get("/add", response_class=HTMLResponse)
async def create_vacancy_page(request: Request, db: AsyncSession = Depends(get_db)):
    head_spec = await user.list(
        db, clauses=[User.user_type == UserType.head_of_department]
    )
    return templates.TemplateResponse(
        "add_vacancy.html", {"request": request, "head_spec": head_spec}
    )


@routers.all_users_router.post(
    "/",
)
async def create_vacancy(
    data_in: VacancyCreateSchema,
    db: AsyncSession = Depends(get_db),
):
    """Создание новой вакансии"""
    created_vacancy = await vacancy.create(db, data_in)
    return created_vacancy


@routers.all_users_router.get("/", response_class=HTMLResponse)
async def get_all_vacancies(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    # Создаем алиас для модели User, используемой в отношении head_of_department
    HeadOfDepartmentAlias = aliased(User)
    query = (
        select(Vacancy, User, HeadOfDepartmentAlias)
        .join(User, Vacancy.recruiter_id == User.id)
        .join(
            HeadOfDepartmentAlias,
            Vacancy.head_of_department_id == HeadOfDepartmentAlias.id,
        )
    )
    results = await db.execute(query)

    vacanciesf = results.scalars().all()
    return templates.TemplateResponse(
        "list_vacancies.html", {"request": request, "vacancies": vacanciesf}
    )


@routers.all_users_router.put("/{vacancy_id}")
async def update_vacancy(
    vacancy_id: int,
    request: Request,
    data_in: VacancyUpdateSchema,
    db: AsyncSession = Depends(get_db),
):
    updated_vacancy = await vacancy.update(db, data_in, vacancy_id)
    return updated_vacancy


@routers.all_users_router.get("/{vacancy_id}/detail", response_class=HTMLResponse)
async def vacancy_detail(
    vacancy_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    HeadOfDepartmentAlias = aliased(User)
    query = (
        select(Vacancy, User, HeadOfDepartmentAlias)
        .join(User, Vacancy.recruiter_id == User.id)
        .join(
            HeadOfDepartmentAlias,
            Vacancy.head_of_department_id == HeadOfDepartmentAlias.id,
        )
        .where(Vacancy.id == vacancy_id)
    )
    result = await db.execute(query)
    found_vacancy = result.scalars().first()
    a = found_vacancy.specialization_list
    t = ",".join(a)

    return templates.TemplateResponse(
        "vacancy_detail.html", {"request": request, "vacancy": found_vacancy, "spec": t}
    )


@routers.all_users_router.post("/{vacancy_id}/add_candidate")
async def create_candidate_phase(
    vacancy_id: int,
    data_in: CandidateAndPhaseCreateSchema,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    candidate_schema = CandidateCreateSchema(
        status=data_in.status,
        first_name=data_in.first_name,
        last_name=data_in.last_name,
        middle_name=data_in.middle_name,
        telegram=data_in.telegram,
        resume_link=data_in.resume_link,
    )
    new_candidate = await candidate.create(db, candidate_schema)
    phase_schema = PhaseCreateSchema(
        phase_type=data_in.phase_type,
        vacancy_id=0,
        candidate_id=0,
        interviewer_id=1,
        result_link=data_in.result_link,
        date=data_in.date,
    )

    phase_schema.candidate_id = new_candidate.id
    phase_schema.vacancy_id = vacancy_id
    new_phase = await phase.create(db, phase_schema)
    return new_phase


@routers.all_users_router.get(
    "/{vacancy_id}/add_candidate", response_class=HTMLResponse
)
async def get_add_candidate_withphase__form(
    vacancy_id: int, request: Request, db: AsyncSession = Depends(get_db)
):
    # Получение списка технических специалистов для выпадающего списка интервьюеров
    tech_specs = await db.execute(
        select(User).where(User.user_type == UserType.technical_specialist)
    )
    tech_specs_list = tech_specs.scalars().all()

    return templates.TemplateResponse(
        "add_candidate_with_phase.html",
        {
            "request": request,
            "vacancy_id": vacancy_id,
            "tech_specs_list": tech_specs_list,
            "candidate_statuses": [CandidateStatus.first_communication],
            "phase_types": [PhaseType.first_communication],
        },
    )
