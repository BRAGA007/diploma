import logging
from typing import AsyncIterator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

import app.db.session


logger = logging.getLogger(__name__)


async def get_db() -> AsyncIterator[AsyncSession]:
    """
    Dependency function that yields db sessions
    """
    async with app.db.session.async_session() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            logger.error("Transaction failed, rolling back")
            await session.rollback()
            raise
