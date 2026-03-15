import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Try to load .env.local if it exists (before importing app settings)
env_local_path = Path(__file__).parent.parent / ".env.local"
if env_local_path.exists():
    with open(env_local_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())

from backend.core.app import settings  # noqa: E402
from backend.models import Base  # noqa: E402

database_url = settings.database_url
target_metadata = Base.metadata
# For migrations, use synchronous psycopg2 driver (not asyncpg) to support multi-statement SQL
if database_url.startswith("postgresql+asyncpg://"):
    database_url = database_url.replace(
        "postgresql+asyncpg://", "postgresql+psycopg2://"
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+psycopg2://"
    )

config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        include_schemas=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url

    connectable = create_engine(
        configuration["sqlalchemy.url"],
        poolclass=pool.NullPool,
        connect_args={"options": "-c search_path=public"},
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
