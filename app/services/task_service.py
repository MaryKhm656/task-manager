from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.crud.constants import ALLOWED_PRIORITIES, ALLOWED_STATUSES
from app.db.models import Category, Task, User
from app.schemas.tasks import TaskCreateData, TaskFilterData, TaskUpdateData


class TaskService:
    @staticmethod
    def _validate_deadline(deadline: Optional[datetime]) -> None:
        if deadline and deadline < datetime.now(timezone.utc):
            raise ValueError("Нельзя установить дедлайн в прошлом")

    @staticmethod
    def _validate_status_priority(status: str, priority: str) -> None:
        if status.lower().strip() not in ALLOWED_STATUSES:
            raise ValueError("Недопустимый статус задачи")
        if priority.lower().strip() not in ALLOWED_PRIORITIES:
            raise ValueError("Недопустимый приоритет задачи")

    @staticmethod
    def create_task(db: Session, user_id: int, task_data: TaskCreateData) -> Task:
        """Method for creating task for user and validate data"""
        if not task_data.title.strip():
            raise ValueError("Название задачи не может быть пустым")

        TaskService._validate_deadline(task_data.deadline)
        TaskService._validate_status_priority(task_data.status, task_data.priority)

        user = db.get(User, user_id)
        if not user:
            raise ValueError("Пользователь не найден")

        # Проверяем уникальность задачи у пользователя
        existing = (
            db.query(Task)
            .filter_by(user_id=user_id, title=task_data.title.strip())
            .first()
        )
        if existing:
            raise ValueError(f"Такая задача у пользователя {user.name} уже существует")

        task = Task(
            user_id=user_id,
            title=task_data.title.strip(),
            description=task_data.description,
            deadline=task_data.deadline,
            status=task_data.status.lower().strip(),
            priority=task_data.priority.lower().strip(),
        )

        if task_data.categories:
            categories = [int(cat_id) for cat_id in task_data.categories]
            found_categories = (
                db.query(Category).filter(Category.id.in_(categories)).all()
            )
            if len(found_categories) != len(set(categories)):
                raise ValueError("Одна или несколько категорий не найдена")
            task.categories = found_categories

        db.add(task)
        db.commit()
        db.refresh(task)

        return (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )

    @staticmethod
    def update_task_full(
        db: Session, user_id: int, task_id: int, update_data: TaskUpdateData
    ) -> Task:
        """Method for updating task"""
        task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача не найдена")

        # Обновляем поля если они переданы
        if update_data.title is not None:
            if not update_data.title.strip():
                raise ValueError("Название задачи не может быть пустым")
            task.title = update_data.title.strip()

        if update_data.description is not None:
            task.description = update_data.description

        if update_data.deadline is not None:
            TaskService._validate_deadline(update_data.deadline)
            task.deadline = update_data.deadline

        if update_data.status is not None:
            clean_status = update_data.status.lower().strip()
            if clean_status not in ALLOWED_STATUSES:
                raise ValueError("Недопустимый статус")
            task.status = clean_status

        if update_data.priority is not None:
            clean_priority = update_data.priority.lower().strip()
            if clean_priority not in ALLOWED_PRIORITIES:
                raise ValueError("Недопустимый приоритет")
            task.priority = clean_priority

        if update_data.categories is not None:
            new_ids = set(map(int, update_data.categories))
            current_ids = set(c.id for c in task.categories)
            if new_ids != current_ids:
                found_cats = db.query(Category).filter(Category.id.in_(new_ids)).all()
                if len(found_cats) != len(new_ids):
                    raise ValueError("Одна или несколько категорий не найдены")
                task.categories = found_cats

        db.commit()
        db.refresh(task)
        return (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )

    @staticmethod
    def get_all_user_tasks(db: Session, user_id: int) -> List[Task]:
        user = db.get(User, user_id)
        if not user:
            raise ValueError("Пользователь с таким ID не найден")

        return (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter_by(user_id=user_id)
            .all()
        )

    @staticmethod
    def get_filtered_tasks(
        db: Session, user_id: int, filters: TaskFilterData
    ) -> List[Task]:
        query = (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.user_id == user_id)
        )

        if filters.status:
            clean_status = filters.status.strip()
            query = query.filter(func.lower(Task.status) == func.lower(clean_status))
        if filters.priority:
            clean_priority = filters.priority.strip()
            query = query.filter(
                func.lower(Task.priority) == func.lower(clean_priority)
            )

        return query.all()

    @staticmethod
    def update_task_categories(
        db: Session, user_id: int, task_id: int, new_categories: list[str]
    ) -> Task:
        """Method for updating categories in task"""
        task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        task.categories = (
            db.query(Category).filter(Category.title.in_(new_categories)).all()
        )
        db.commit()
        db.refresh(task)
        task_with_categories = (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories

    @staticmethod
    def update_task_status(
        db: Session, user_id: int, task_id: int, new_status: str
    ) -> Task:
        """Update task status"""
        task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        clean_status = new_status.lower().strip()
        if clean_status not in ALLOWED_STATUSES:
            raise ValueError("Недопустимый статус задачи")
        task.status = clean_status
        db.commit()
        db.refresh(task)
        task_with_categories = (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories

    @staticmethod
    def update_task_priority(
        db: Session, user_id: int, task_id: int, new_priority: str
    ) -> Task:
        """Update task priority"""
        task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        clean_priority = new_priority.lower().strip()
        if clean_priority not in ALLOWED_PRIORITIES:
            raise ValueError("Недопустимый формат приоритета")
        task.priority = clean_priority
        db.commit()
        db.refresh(task)
        task_with_categories = (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories

    @staticmethod
    def update_task_description(
        db: Session, user_id: int, task_id: int, new_description: str
    ) -> Task:
        """Update task description"""
        task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        task.description = new_description
        db.commit()
        db.refresh(task)
        task_with_categories = (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories

    @staticmethod
    def update_deadline(
        db: Session, user_id: int, task_id: int, new_deadline: datetime
    ) -> Task:
        """Update task deadline"""
        task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")

        if new_deadline < datetime.now(timezone.utc):
            raise ValueError("Дедлайн не может быть в прошлом")

        task.deadline = new_deadline
        db.commit()
        db.refresh(task)
        task_with_categories = (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories

    @staticmethod
    def get_user_task_by_id(db: Session, user_id: int, task_id: int) -> Task:
        """Getting user task by task id"""
        user = db.get(User, user_id)
        if not user:
            raise ValueError("Пользователь с таким ID не найден")

        task_by_id = (
            db.query(Task)
            .options(selectinload(Task.categories))
            .filter_by(user_id=user_id, id=task_id)
            .first()
        )
        if not task_by_id:
            raise ValueError("Задача не найдена")
        return task_by_id

    @staticmethod
    def delete_task(db: Session, user_id: int, task_id: int) -> str:
        """Delete task by id and return success message"""
        task = db.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        db.delete(task)
        db.commit()
        return "Задача успешно удалена"
