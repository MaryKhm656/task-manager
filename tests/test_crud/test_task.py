import pytest

from app.schemas.tasks import TaskCreateData
from app.services.task_service import TaskService
from tests.constants.data import (
    MessageForCheck,
    PriorityParameters,
    StatusParameters,
    TaskParameters,
)


def test_create_task_with_required_field(data_for_test):
    """
    Scenario

    1. Create task with required field(title)
    2. Check task was saved with given title and default parameters
    """
    user, _, db = data_for_test
    task_data = TaskCreateData(title=TaskParameters.TITLE)
    task = TaskService.create_task(db, user.id, task_data)
    assert (
        task.title == TaskParameters.TITLE
    ), f"{task.title} not equal to {TaskParameters.TITLE}"
    assert (
        task.description is None
    ), f"Task description is not None. Was: {task.description}"
    assert task.deadline is None, f"Task deadline is not None. Was: {task.deadline}"
    assert task.categories == [], (
        f"Task categories is not empty. Was: "
        f"{[category.title for category in task.categories]}"
    )
    assert (
        task.status == StatusParameters.NOT_COMPLETED
    ), f"{task.status} not equal to {StatusParameters.NOT_COMPLETED}"
    assert (
        task.priority == PriorityParameters.MIDDLE
    ), f"{task.priority} not equal to {PriorityParameters.MIDDLE}"
    assert task.user_id == user.id, f"{task.user_id} not equal to {user.id}"
    TaskService.delete_task(db, user.id, task.id)


def test_create_task_with_all_fields(data_for_test):
    """
    Scenario

    1. Create task with all filling fields
    2. Check creating task data equal to expected task data
    """
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
    assert (
        task.title == TaskParameters.TITLE
    ), f"{task.title} not equal to {TaskParameters.TITLE}"
    assert (
        task.description == TaskParameters.DESCRIPTION
    ), f"{task.description} not equal to {TaskParameters.DESCRIPTION}"
    assert (
        task.deadline == TaskParameters.DEADLINE
    ), f"{task.deadline} not equal to {TaskParameters.DEADLINE}"
    assert task.categories == categories, f"{task.categories} not equal to {categories}"
    assert (
        task.status == TaskParameters.STATUS
    ), f"{task.status} not equal to {TaskParameters.STATUS}"
    assert (
        task.priority == TaskParameters.PRIORITY
    ), f"{task.priority} not equal to {TaskParameters.PRIORITY}"
    TaskService.delete_task(db, user.id, task.id)


def test_delete_task(create_default_test_task):
    """
    Scenario

    1. Create default test task
    2. Delete task from database
    3. Check task not found
    """
    task, user, categories, db = create_default_test_task
    success_message = TaskService.delete_task(db, user.id, task.id)
    assert (
        success_message == MessageForCheck.TASK_SUCCESS_DELETE
    ), f"WARNING! {success_message} not equal to {MessageForCheck.TASK_SUCCESS_DELETE}"
    with pytest.raises(ValueError, match=MessageForCheck.TASK_NOT_FOUND):
        TaskService.get_user_task_by_id(db, user.id, task.id)
