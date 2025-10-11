from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.models import Base

engine = create_engine("sqlite:///./test.db")

SessionLocal = sessionmaker(bind=engine)


def init_test_db():
    Base.metadata.create_all(bind=engine)


def drop_test_db():
    Base.metadata.drop_all(bind=engine)
