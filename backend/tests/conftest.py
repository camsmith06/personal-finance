import os
from collections.abc import Generator
from pathlib import Path

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:postgres@localhost:5432/personal_finance",
)

import pytest
from alembic.config import Config
from sqlalchemy.orm import Session

from alembic import command
from app.database import engine


@pytest.fixture(scope="session", autouse=True)
def apply_migrations() -> None:
    alembic_config = Config(str(Path(__file__).parents[1] / "alembic.ini"))
    command.upgrade(alembic_config, "head")


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    try:
        yield session
    finally:
        session.close()
        if transaction.is_active:
            transaction.rollback()
        connection.close()
