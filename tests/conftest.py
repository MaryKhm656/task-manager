from typing import Any, Generator

import pytest

from app.db.models import Category, Task, User, task_categories_association
from app.services.category_service import CategoryService
from app.services.user_service import UserService
from tests.constants.data import AccountParameters, CategoryParameters
from tests.constants.db import SessionLocal, drop_test_db, init_test_db


@pytest.fixture
def init_db():
    init_test_db()
    db = SessionLocal()
    yield db
    drop_test_db()


@pytest.fixture
def data_for_test(init_db) -> Generator[tuple[User, list[Any], Any], Any, None]:
    db = init_db
    user = UserService.create_user(
        db,
        AccountParameters.USERNAME,
        AccountParameters.EMAIL,
        AccountParameters.PASSWORD,
    )
    categories = []
    for category in CategoryParameters.ALL_CATEGORIES:
        category = CategoryService.create_category(db, category)
        categories.append(category)
    yield user, categories, db
    UserService.delete_user(db, user.id)
