import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import telebot
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import HTMLResponse

from app import settings
from app.api.deps import get_db
from app.core.routes import AuthApiRouters
from app.crud import candidate, phase, vacancy, user
from app.enums import UserType, PhaseType
from app.models import Candidate, Phase, User, Vacancy
from app.schemas.models import (
    PhaseCreateSchema,
    PhaseCandidateCreateSchema,
    PhaseUpdateSchema,
    PhaseFeedbackSendSchema,
    PhaseFeedbackSendFlagSchema,
)

routers = AuthApiRouters(prefix="/phases", tags=["phases"])
templates = Jinja2Templates(directory="app/templates")


def send_email(to_address, subject, body):
    # Информация о письме
    from_address = settings.smtp_user

    # Создание объекта MIMEMultipart
    msg = MIMEMultipart()
    msg["From"] = from_address
    msg["To"] = to_address
    msg["Subject"] = subject

    # Добавление тела письма в формате HTML
    msg.attach(MIMEText(body, "html"))

    try:
        # Установка соединения с сервером
        server = smtplib.SMTP_SSL(settings.smtp_server, settings.smtp_port)
        server.login(settings.smtp_user, settings.smtp_password)

        # Отправка письма
        server.sendmail(from_address, to_address, msg.as_string())

        # Завершение соединения
        server.quit()
        print("Письмо успешно отправлено!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")


@routers.all_users_router.get(
    "/",
)
async def list_phases(request: Request, db: AsyncSession = Depends(get_db)):
    """Вывод списка всех собеседований"""
    query = (
        select(Phase, User, Candidate, Vacancy)
        .join(User, Phase.interviewer_id == User.id)
        .join(
            Candidate,
            Phase.candidate_id == Candidate.id,
        )
        .join(
            Vacancy,
            Phase.vacancy_id == Vacancy.id,
        )
    )
    result = await db.execute(query)
    found_phases = result.scalars().all()
    return templates.TemplateResponse(
        "list_phases.html", {"request": request, "phases": found_phases}
    )


@routers.all_users_router.get("/candidate/{candidate_id}/technical")
async def read_root(
    request: Request, candidate_id: int, db: AsyncSession = Depends(get_db)
):
    vacancies = await vacancy.list(db)  # Получение списка вакансий
    tech_spec = await user.list(
        db, clauses=[User.user_type == UserType.technical_specialist]
    )

    return templates.TemplateResponse(
        "add_technical_phase.html",
        {
            "request": request,
            "vacancies": vacancies,
            "tech_spec": tech_spec,
            "candidate_id": candidate_id,
        },
    )


@routers.all_users_router.post(
    "/candidate/{candidate_id}/technical",
)
async def create_tech_phase(
    *,
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    data_in: PhaseCandidateCreateSchema,
):
    """Создание нового этапа собеседования"""
    phase_schema = PhaseCreateSchema(
        phase_type=PhaseType.technical_interview,
        vacancy_id=data_in.vacancy_id,
        candidate_id=candidate_id,
        interviewer_id=data_in.interviewer_id,
        result_link=None,
        date=data_in.date,
    )
    created_phase = await phase.create(
        db,
        phase_schema,
    )
    await candidate.set_waiting_tech_stage_status(db, candidate_id)
    # Отправка письма при успешном создании этапа собеседования
    candidate_info = await candidate.get(db, candidate_id)
    interviewer = await user.get(db, data_in.interviewer_id)
    to_address = interviewer.email
    subject = "Новое Техническое интервью назначено"
    body = f"""
            <html>
            <body>
                <h1>Новое Техническое интервью</h1>
                <p>Уважаемый {interviewer.first_name} {interviewer.last_name},</p>
                <p>Вы назначены на проведение технического интервью для кандидата {candidate_info.first_name} {candidate_info.last_name}.</p>
                <p><b>Дата:</b> {data_in.date}</p>
                <p><b>Ссылка на вакансию:</b> <a href="http://localhost:8088/api/v1/vacancies/{data_in.vacancy_id}/detail">Вакансия</a></p>
                <p><b>Ссылка на кандидата:</b> <a href="http://localhost:8088/api/v1/candidates/{candidate_id}/">Инфо о кандидате </a></p>
                <p><b>Ссылка на заполнение результатов:</b> <a href="http://localhost:8088/api/v1/phases/{created_phase.id}/edit">Результаты</a></p>
            </body>
            </html>
            """

    send_email(to_address, subject, body)
    return created_phase


@routers.all_users_router.get("/candidate/{candidate_id}/final")
async def read_root(
    request: Request, candidate_id: int, db: AsyncSession = Depends(get_db)
):
    vacancies = await vacancy.list(db)  # Получение списка вакансий
    head_spec = await user.list(
        db, clauses=[User.user_type == UserType.head_of_department]
    )

    return templates.TemplateResponse(
        "add_final_phase.html",
        {
            "request": request,
            "vacancies": vacancies,
            "head_spec": head_spec,
            "candidate_id": candidate_id,
        },
    )


@routers.all_users_router.post(
    "/candidate/{candidate_id}/final",
)
async def create_final_phase(
    *,
    candidate_id: int,
    db: AsyncSession = Depends(get_db),
    data_in: PhaseCandidateCreateSchema,
):
    """Создание нового этапа собеседования"""
    phase_schema = PhaseCreateSchema(
        phase_type=PhaseType.final_interview,
        vacancy_id=data_in.vacancy_id,
        candidate_id=candidate_id,
        interviewer_id=data_in.interviewer_id,
        result_link=None,
        date=data_in.date,
    )
    created_phase = await phase.create(
        db,
        phase_schema,
    )
    await candidate.set_waiting_final_stage_status(db, candidate_id)
    # Отправка письма при успешном создании этапа собеседования
    candidate_info = await candidate.get(db, candidate_id)
    interviewer = await user.get(db, data_in.interviewer_id)
    to_address = interviewer.email
    subject = "Новое Финальное интервью назначено"
    body = f"""
        <html>
        <body>
            <h1>Новое Финальное интервью</h1>
            <p>Уважаемый {interviewer.first_name} {interviewer.last_name},</p>
            <p>Вы назначены на проведение финального интервью для кандидата {candidate_info.first_name} {candidate_info.last_name}.</p>
            <p><b>Дата:</b> {data_in.date}</p>
            <p><b>Ссылка на вакансию:</b> <a href="http://localhost:8088/api/v1/vacancies/{data_in.vacancy_id}/detail">Вакансия</a></p>
            <p><b>Ссылка на кандидата:</b> <a href="http://localhost:8088/api/v1/candidates/{candidate_id}/">Инфо о кандидате </a></p>
            <p><b>Ссылка на заполнение результатов:</b> <a href="http://localhost:8088/api/v1/phases/{created_phase.id}/edit">Результаты</a></p>
        </body>
        </html>
        """

    send_email(to_address, subject, body)
    return created_phase


@routers.all_users_router.put(
    "/{phase_id}/edit",
)
async def edit_phase(
    *, phase_id: int, db: AsyncSession = Depends(get_db), data_in: PhaseUpdateSchema
):
    """Создание нового этапа собеседования"""
    updated_phase = await phase.update(db, data_in, phase_id)
    if updated_phase.phase_type == PhaseType.technical_interview:
        if data_in.passed is True:
            await candidate.set_success_tech_stage_status(
                db, updated_phase.candidate_id
            )
        else:
            await candidate.set_failed_tech_stage_status(db, updated_phase.candidate_id)
    if updated_phase.phase_type == PhaseType.final_interview:
        if data_in.passed is True:
            await candidate.set_success_final_stage_status(
                db, updated_phase.candidate_id
            )
        else:
            await candidate.set_failed_final_stage_status(
                db, updated_phase.candidate_id
            )

    candidate_info = await candidate.get(db, updated_phase.candidate_id)
    vacancy_info = await vacancy.get(db, updated_phase.vacancy_id)
    recruiter = await user.get(db, vacancy_info.recruiter_id)
    to_address = recruiter.email
    subject = "Обратная связь по кандидату"
    body = f"""
            <html>
            <body>
                <h1>Обратная связь по кандидату</h1>
                <p>Уважаемый {recruiter.first_name} {recruiter.last_name},</p>
                <p>Кандидат {candidate_info.first_name} {candidate_info.last_name} прошел собеседование.</p>
                <p><b>С результатами можно ознакомиться:</b>  <a href="http://localhost:8088/api/v1/candidates/{updated_phase.candidate_id}/">Инфо о кандидате </a></p>
            </body>
            </html>
            """

    send_email(to_address, subject, body)
    return updated_phase


@routers.all_users_router.get("/{phase_id}/edit", response_class=HTMLResponse)
async def get_edit_phase(
    request: Request, phase_id: int, db: AsyncSession = Depends(get_db)
):
    phase_data = await phase.get(db, phase_id)
    return templates.TemplateResponse(
        "edit_phase.html", {"request": request, "phase": phase_data}
    )


@routers.all_users_router.get("/{phase_id}/send_feedback", response_class=HTMLResponse)
async def send_feedback(
    request: Request,
    phase_id: int,
    db: AsyncSession = Depends(get_db),
):
    phase_data = await phase.get(db, phase_id)
    return templates.TemplateResponse(
        "send_feedback.html", {"request": request, "phase": phase_data}
    )


@routers.all_users_router.post("/{phase_id}/send_feedback")
async def send_feedback(
    request: Request,
    phase_id: int,
    data_in: PhaseFeedbackSendSchema,
    db: AsyncSession = Depends(get_db),
):

    update_schema = PhaseFeedbackSendFlagSchema(feedback_send=True)

    bot = telebot.TeleBot("")

    phase_info = await phase.get(db, phase_id)
    updated_phase = await phase.update(db, update_schema, phase_id)
    candidate_info = await candidate.get(db, phase_info.candidate_id)
    if phase_info.phase_type == PhaseType.final_interview:
        await candidate.set_waiting_offer_status(db, candidate_info.id)
    bot.send_message(495520145, data_in.feedback)
    return updated_phase
