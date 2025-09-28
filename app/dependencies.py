from typing import Generator

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.crud.auth import get_current_user_from_cookie
from app.db.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Dependency to receive session for DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_template_user(request: Request):
    """Returned user or None"""
    try:
        current_user = get_current_user_from_cookie(request)
        return current_user
    except HTTPException:
        return None
