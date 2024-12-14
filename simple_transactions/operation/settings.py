import enum
from pathlib import Path
from tempfile import gettempdir

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from yarl import URL

TEMP_DIR = Path(gettempdir())


class LogLevel(str, enum.Enum):
    """Possible log levels."""

    NOTSET = "NOTSET"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"


class Settings(BaseSettings):
    """
    Application settings.

    These parameters can be configured
    with environment variables.
    """

    microservice_location: str = "simple_transactions/operation"

    host: str = "127.0.0.1"
    port: int = 8000
    # quantity of workers for uvicorn
    workers_count: int = 1
    # Enable uvicorn reloading
    reload: bool = False

    SIMPLE_TRANSACTIONS_AUTH_SECRET_KEY: str = Field(
        alias="SIMPLE_TRANSACTIONS_AUTH_SECRET_KEY"
    )
    SIMPLE_TRANSACTIONS_AUTH_ENCRYPT_ALGORITHM: str = Field(
        alias="SIMPLE_TRANSACTIONS_AUTH_ENCRYPT_ALGORITHM"
    )
    SIMPLE_TRANSACTIONS_AUTH_DEFAULT_JWT_EXPIRES_SECONDS: int = Field(
        alias="SIMPLE_TRANSACTIONS_AUTH_DEFAULT_JWT_EXPIRES_SECONDS"
    )

    # Current environment
    environment: str = "dev"

    log_level: LogLevel = LogLevel.INFO
    # Variables for the database
    db_host: str = "localhost"
    db_port: int = 5432
    db_user: str = "simple_transactions"
    db_pass: str = "simple_transactions"
    db_base: str = "simple_transactions"
    db_echo: bool = False

    # Location of alembic.ini
    alembic_ini: str = "alembic.ini"
    alembic_folder: str = "simple_transactions/operation/migration"

    def build_relative_location_to(self, filename: str) -> Path:
        return Path(self.microservice_location, filename)

    @property
    def sync_db_url(self) -> URL:
        """
        Assemble database URL from settings.
        Using sync scheme without asyncpg

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    @property
    def db_url(self) -> URL:
        """
        Assemble database URL from settings.

        :return: database URL.
        """
        return URL.build(
            scheme="postgresql+asyncpg",
            host=self.db_host,
            port=self.db_port,
            user=self.db_user,
            password=self.db_pass,
            path=f"/{self.db_base}",
        )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SIMPLE_TRANSACTIONS_",
        env_file_encoding="utf-8",
    )


settings = Settings()
