import asyncio
import logging

from sqlalchemy.sql import text
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed

from app.db import async_session


logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def main() -> None:
    logger.info("Initializing DB connection")
    try:
        async with async_session() as session:
            await session.execute(text("SELECT 1"))
    except Exception as error:
        logger.error(error)
        raise error
    logger.info("DB connection successful")


if __name__ == "__main__":
    logger.info("Initializing app")
    loop.run_until_complete(main())
