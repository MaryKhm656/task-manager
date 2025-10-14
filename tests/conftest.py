from typing import Any, Generator

import pytest

from app.db.models import Category, Task, User, task_categories_association
from app.schemas.tasks import TaskCreateData
from app.services.category_service import CategoryService
from app.services.task_service import TaskService
from app.services.user_service import UserService
from tests.constants.data import AccountParameters, CategoryParameters, TaskParameters
from tests.constants.db import SessionLocal, drop_test_db, init_test_db


@pytest.fixture
def init_db():
    init_test_db()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
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
    CategoryService.delete_categories_list(db, [category.id for category in categories])


@pytest.fixture
def create_default_test_user(init_db):
    db = init_db
    user = UserService.create_user(
        db,
        AccountParameters.USERNAME,
        AccountParameters.EMAIL,
        AccountParameters.PASSWORD,
    )
    return db, user


@pytest.fixture
def create_default_test_categories(init_db):
    db = init_db
    categories = []
    for category in CategoryParameters.ALL_CATEGORIES:
        category = CategoryService.create_category(db, category)
        categories.append(category)
    return db, categories


@pytest.fixture
def create_default_test_task(data_for_test):
    user, categories, db = data_for_test
    task_data = TaskCreateData(
        title=TaskParameters.TITLE,
        description=TaskParameters.DESCRIPTION,
        deadline=TaskParameters.DEADLINE,
        categories=[category.id for category in categories],
        status=TaskParameters.STATUS,
        priority=TaskParameters.PRIORITY,
    )
    task = TaskService.create_task(db, user.id, task_data)
    return task, user, categories, db
