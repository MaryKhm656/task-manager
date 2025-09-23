from typing import Generator

from sqlalchemy.orm import Session

from app.db.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency to receive session for DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
