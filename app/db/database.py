import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def get_database_url() -> str:
    """Reading environment from .env and returned database url"""

    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")

    db_host = (
        "db"
        if os.getenv("DOCKER_CONTAINER") or os.getenv("KUBERNETES_SERVICE_HOST")
        else "localhost"
    )

    return (
        f"postgresql+psycopg2:/" f"/{db_user}:{db_password}@{db_host}:5432/{db_name}"
    )  # noqa: E231


DATABASE_URL = get_database_url()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
