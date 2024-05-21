from fastapi import Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.routes import AuthApiRouters
from app.crud import candidate
from app.models import Candidate, Phase, User, Vacancy
from app.schemas.models import (
    CandidateCreateSchema,
)

routers = AuthApiRouters(prefix="/candidates", tags=["candidates"])
templates = Jinja2Templates(directory="app/templates")


@routers.all_users_router.get("/add", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("add_candidate.html", {"request": request})


@routers.all_users_router.post(
    "/",
)
async def create_candidate(
    *, db: AsyncSession = Depends(get_db), data_in: CandidateCreateSchema
):
    """Создание нового кандидата"""

    created_candidate = await candidate.create(
        db,
        data_in,
    )
    return created_candidate


@routers.all_users_router.get(
    "/",
)
async def list_candidates(request: Request, db: AsyncSession = Depends(get_db)):
    """Вывод списка кандидатов"""
    found_candidates = await candidate.list(db)
    return templates.TemplateResponse(
        "list_candidates.html", {"request": request, "candidates": found_candidates}
    )


@routers.all_users_router.post(
    "/",
)
async def create_candidate(
    *, db: AsyncSession = Depends(get_db), data_in: CandidateCreateSchema
):
    """Создание нового кандидата"""

    created_candidate = await candidate.create(
        db,
        data_in,
    )
    return created_candidate


@routers.all_users_router.get(
    "/{candidate_id}",
)
async def get_candidate(
    request: Request, candidate_id: int, db: AsyncSession = Depends(get_db)
):
    """Вывод списка кандидатов"""
    found_candidate = await candidate.get(db, candidate_id)

    query = (
        select(Phase, User, Candidate, Vacancy)
        .join(User, Phase.interviewer_id == User.id)
        .join(
            Candidate,
            Phase.candidate_id == Candidate.id,
        )
        .join(Vacancy, Phase.vacancy_id == Vacancy.id)
        .where(Candidate.id == candidate_id)
    )
    result = await db.execute(query)
    candidate_phases = result.scalars().all()

    return templates.TemplateResponse(
        "candidate_detail.html",
        {
            "request": request,
            "candidate": found_candidate,
            "candidate_phases": candidate_phases,
        },
    )
