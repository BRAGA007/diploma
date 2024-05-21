from typing import TYPE_CHECKING, Any, Optional
from urllib.parse import quote_plus

from pydantic import (
    EmailStr,
    model_validator,
)
from pydantic_settings import BaseSettings

if TYPE_CHECKING:
    PostgresDsn = str
else:
    from pydantic import PostgresDsn

try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        pass



class Settings(BaseSettings):

    postgres_host: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: str = "5432"
    postgres_schema: str = "portal"

    database_uri: Optional[PostgresDsn] = None

    @model_validator(mode="after")
    def assemble_db_connection(self) -> Any:
        self.database_uri = (
            f"postgresql+asyncpg://{quote_plus(self.postgres_user)}:{quote_plus(self.postgres_password)}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )
        return self

    first_superuser_email: EmailStr
    first_superuser_password: str

    logging_level: str = "INFO"
    smtp_server:str = "smtp.mail.ru"
    smtp_port:int = 465
    smtp_user:str = ""
    smtp_password:str = ""

    tg_hash: str = ""
    tg_app_id: str = ""
    tg_token: str = ""

settings = Settings()

