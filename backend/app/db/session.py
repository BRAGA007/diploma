from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings


engine = create_async_engine(
    str(settings.database_uri),  # Какая-то несовместимость либ, лучше в строку передавать
    echo=(settings.logging_level == "DEBUG"),
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#using-multiple-asyncio-event-loops
    poolclass=NullPool,
)
async_session = async_sessionmaker(engine, expire_on_commit=False)
