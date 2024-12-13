from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from simple_transactions.auth.db.models import load_all_models
from simple_transactions.auth.settings import settings

config = context.config
config.set_main_option("sqlalchemy.url", str(settings.sync_db_url))

# if config.config_file_name is not None:
#     fileConfig(config.config_file_name, disable_existing_loggers=False)

load_all_models()
from simple_transactions.auth.db.meta import meta

target_metadata = meta


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    connection = engine.connect()
    context.configure(connection=connection, target_metadata=target_metadata)

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
