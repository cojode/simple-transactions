from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from alembic import command
from alembic.config import Config

from simple_transactions.auth.settings import settings

from sqlalchemy import create_engine, text

from loguru import logger

from simple_transactions.auth.log import configure_logging


def _test_db_connection():
    engine = create_engine(str(settings.sync_db_url))
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            logger.info("Database connection is healthy.")
    finally:
        engine.dispose()


def _setup_db(app: FastAPI) -> None:  # pragma: no cover
    """
    Creates connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(str(settings.db_url), echo=settings.db_echo)
    session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory


def _run_migrations() -> None:  # pragma: no cover
    alembic_cfg = Config(str(settings.build_relative_location_to(settings.alembic_ini)))
    alembic_cfg.set_main_option("script_location", settings.alembic_folder)
    logger.info("Attempting migration with alembic upgrade runtime call.")
    command.upgrade(alembic_cfg, "head")
    logger.info("Alembic call succeeded: migration succesfull.")


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None, None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """
    configure_logging()
    app.middleware_stack = None
    _setup_db(app)
    _test_db_connection()
    _run_migrations()

    app.middleware_stack = app.build_middleware_stack()

    yield
    await app.state.db_engine.dispose()
