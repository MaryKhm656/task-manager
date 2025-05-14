from sqlalchemy import func
from sqlalchemy.orm import selectinload
from app.db.models import User, Task, Category
from app.db.database import SessionLocal
from datetime import datetime, timezone
from app.crud.constants import ALLOWED_STATUSES, ALLOWED_PRIORITIES
from app.crud.security import hash_password, verify_password
from typing import Optional

def create_user(name: str, email: str, password: str):
    if len(name) < 2:
        raise ValueError("Имя пользователя не может быть меньше двух символов")

    session = SessionLocal()
    try:
        if "@" not in email and "." not in email:
            raise ValueError("Некорректный email")
        existing_user = session.query(User).filter_by(email=email).first()
        if existing_user:
            raise ValueError("Аккаунт с таким email уже существует!")

        hashed_pwd = hash_password(password)
        user = User(name=name.strip(), email=email, password=hashed_pwd)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    finally:
        session.close()


def login_user(email: str, password: str):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(email=email).first()
        if not user or not verify_password(password, user.password):
            raise ValueError("Неверный email или пароль")
        return user
    finally:
        session.close()


def create_task(user_id: int, title: str, description: str = None, deadline: datetime = None, categories: list[str] = None, status: str = "не выполнена", priority: str = "средний"):
    if not title.strip():
        raise ValueError("Название задачи не может быть пустым")

    if isinstance(deadline, str):
        if not deadline.strip():
            deadline = None
        else:
            try:
                deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M")
            except ValueError:
                raise ValueError("Неверный формат даты. Ожидается формат: 'YYYY-MM-DD HH:MM'")
    if deadline and deadline < datetime.now():
        raise ValueError("Нельзя установить дедлайн в прошлом")

    session = SessionLocal()
    try:
        user = session.get(User, user_id)
        if not user:
            raise ValueError("Пользователь не найден")

        existing = session.query(Task).filter_by(user_id=user_id, title=title).first()
        if existing:
            raise ValueError(f"Такая задача у пользователя {user.name} уже существует")

        clean_status = status.lower().strip()
        clean_priority = priority.lower().strip()

        if clean_status not in ALLOWED_STATUSES:
            raise ValueError("Недопустимый статус задачи")
        if clean_priority not in ALLOWED_PRIORITIES:
            raise ValueError("Недопустимый приоритет задачи")

        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description,
            deadline=deadline,
            status=clean_status,
            priority=clean_priority
        )
        
        if categories:
            categories = [int(cat_id) for cat_id in categories]
            found_categories = session.query(Category).filter(Category.id.in_(categories)).all()
            if len(found_categories) != len(set(categories)):
                raise ValueError("Одна или несколько категорий не найдена")
            task.categories = found_categories
        
        session.add(task)
        session.commit()
        session.refresh(task)
        task_with_categories = (
            session.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )

        return task_with_categories
    finally:
        session.close()


def create_category(title: str):
    clean_title = title.lower().strip()
    if not clean_title:
        raise ValueError("Название категории не может быть пустым")

    session = SessionLocal()
    try:
        existing = session.query(Category).filter_by(title=clean_title).first()
        if existing:
            raise ValueError("Такая категория уже существует")

        category = Category(title=clean_title)
        session.add(category)
        session.commit()
        session.refresh(category)
        return category
    finally:
        session.close()
        
        
def update_task_categories(user_id: int, task_id: int, new_categories: list[str]):
    session = SessionLocal()
    try:
        task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        task.categories = session.query(Category).filter(Category.title.in_(new_categories)).all()
        session.commit()
        session.refresh(task)
        task_with_categories = (
            session.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories
    finally:
        session.close()
        
        
def update_task_status(user_id: int, task_id: int, new_status: str):
    session = SessionLocal()
    try:
        task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        clean_status = new_status.lower().strip()
        if clean_status not in ALLOWED_STATUSES:
            raise ValueError("Недопустимый статус задачи")
        task.status = clean_status
        session.commit()
        session.refresh(task)
        task_with_categories = (
            session.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories
    finally:
        session.close()
        
        
def update_task_priority(user_id: int, task_id: int, new_priority: str):
    session = SessionLocal()
    try:
        task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        clean_priority = new_priority.lower().strip()
        if clean_priority not in ALLOWED_PRIORITIES:
            raise ValueError("Недопустимый формат приоритета")
        task.priority = clean_priority
        session.commit()
        session.refresh(task)
        task_with_categories = (
            session.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories
    finally:
        session.close()
        
        
def update_description(user_id: int, task_id: int, new_description: str):
    session = SessionLocal()
    try:
        task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        task.description = new_description
        session.commit()
        session.refresh(task)
        task_with_categories = (
            session.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories
    finally:
        session.close()


def update_deadline(user_id: int, task_id: int, new_deadline: datetime):
    if isinstance(new_deadline, str):
        try:
            new_deadline = datetime.strptime(new_deadline, "%Y-%m-%d %H:%M")
            new_deadline = new_deadline.replace(tzinfo=timezone.utc)
        except ValueError:
            raise ValueError("Неверный формат даты. Используй 'YYYY-MM-DD HH:MM'")

    session = SessionLocal()
    try:
        task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")

        if new_deadline < datetime.now(timezone.utc):
            raise ValueError("Дедлайн не может быть в прошлом")

        task.deadline = new_deadline
        session.commit()
        session.refresh(task)
        task_with_categories = (
            session.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories
    finally:
        session.close()

def update_task_full(
        user_id: int,
        task_id: int,
        title: str = None,
        status: str = None,
        priority: str = None,
        deadline: str = None,
        description: str = None,
        categories: list[int] = None
):
    session = SessionLocal()
    try:
        task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача не найдена")
        
        if title and task.title != title:
            if not title.strip():
                raise ValueError("Название задачи не может быть пустым")
            task.title = title.strip()
            
        if description is not None and task.description != description:
            task.description = description

        if deadline:
            deadline = deadline.replace("T", " ")
            try:
                parsed_deadline = datetime.strptime(deadline, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                if task.deadline != parsed_deadline:
                    if parsed_deadline < datetime.now(timezone.utc):
                        raise ValueError("Дедлайн не может быть в прошлом")
                    task.deadline = parsed_deadline
            except ValueError:
                raise ValueError("Неверный формат даты")
            
        if status and task.status != status.lower().strip():
            clean_status = status.lower().strip()
            if clean_status not in ALLOWED_STATUSES:
                raise ValueError("Недопустимый статус")
            task.status = clean_status
            
        if priority and task.priority != priority.lower().strip():
            clean_priority = priority.lower().strip()
            if clean_priority not in ALLOWED_PRIORITIES:
                raise ValueError("Недопустимый приоритет")
            task.priority = clean_priority
            
        if categories is not None:
            new_ids = set(map(int, categories))
            current_ids = set([c.id for c in task.categories])
            if new_ids != current_ids:
                found_cats = session.query(Category).filter(Category.id.in_(new_ids)).all()
                if len(found_cats) != len(new_ids):
                    raise ValueError("Одна или несколько категорий не найдены")
                task.categories = found_cats
                
        session.commit()
        session.refresh(task)
        task_with_categories = (
            session.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.id == task.id)
            .first()
        )
        return task_with_categories
    finally:
        session.close()

        

def get_all_user_tasks(user_id: int):
    session = SessionLocal()
    try:
        user = session.get(User, user_id)
        if not user:
            raise ValueError("Пользователь с таким ID не найден")

        all_tasks = (
            session.query(Task)
            .options(selectinload(Task.categories))
            .filter_by(user_id=user_id)
            .all()
        )
        return all_tasks
    finally:
        session.close()

def get_user_task_by_id(user_id: int, task_id: int):
    session = SessionLocal()
    try:
        user = session.get(User, user_id)
        if not user:
            raise ValueError("Пользователь с таким ID не найден")
        
        task_by_id = session.query(Task).options(selectinload(Task.categories)).filter_by(user_id=user_id, id=task_id).first()
        if not task_by_id:
            raise ValueError("Задача не найдена")
        return task_by_id
    finally:
        session.close()

def get_filtered_tasks(user_id: int, status: Optional[str] = None, priority: Optional[str] = None):
    session = SessionLocal()
    try:
        query = (
            session.query(Task)
            .options(selectinload(Task.categories))
            .filter(Task.user_id == user_id)
        )

        if status:
            clean_status = status.strip()
            query = query.filter(func.lower(Task.status) == func.lower(clean_status))
        if priority:
            clean_priority = priority.strip()
            query = query.filter(func.lower(Task.priority) == func.lower(clean_priority))
        tasks = query.all()
        return tasks
    finally:
        session.close()


def get_all_categories():
    session = SessionLocal()
    try:
        categories = session.query(Category).all()
        return categories
    finally:
        session.close()
        
        
def delete_task(user_id: int, task_id: int):
    session = SessionLocal()
    try:
        task = session.query(Task).filter_by(id=task_id, user_id=user_id).first()
        if not task:
            raise ValueError("Задача с таким ID у пользователя не найдена")
        session.delete(task)
        session.commit()
        return "Задача успешно удалена"
    finally:
        session.close()
        
        
def delete_user(user_id: int):
    session = SessionLocal()
    try:
        user = session.get(User, user_id)
        if not user:
            raise ValueError("Пользователь с таким ID не найден")
        session.delete(user)
        session.commit()
        return "Пользователь успешно удален"
    finally:
        session.close()
        
        
def delete_category(category_id: int):
    session = SessionLocal()
    try:
        category = session.get(Category, category_id)
        if not category:
            raise ValueError("Категория с таким ID не найдена")
        session.delete(category)
        session.commit()
        return "Категория успешно удалена"
    finally:
        session.close()
        
def delete_categories_list(category_ids: list[int]):
    session = SessionLocal()
    try:
        for category_id in category_ids:
            category = session.get(Category, category_id)
            if not category:
                raise ValueError(f"Категория с {category_id} не найдена")
            session.delete(category)
        session.commit()
        return "Категории успешно удалены"
    finally:
        session.close()