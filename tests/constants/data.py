from dataclasses import dataclass
from datetime import datetime, timedelta


class MessageForCheck:
    TASK_SUCCESS_DELETE = "Задача успешно удалена"
    TASK_NOT_FOUND = "Задача не найдена"
    USER_SUCCESS_DELETE = "Пользователь успешно удален"
    USER_NOT_FOUND = "Пользователь с таким ID не найден"
    CATEGORY_SUCCESS_DELETE = "Категория успешно удалена"


class AccountParameters:
    USERNAME = "Test Username"
    EMAIL = "test@email.com"
    PASSWORD = "TestPassword"


class StatusParameters:
    NOT_COMPLETED = "не выполнена"
    IN_PROGRESS = "в процессе"
    COMPLETED = "выполнена"


class PriorityParameters:
    LOW = "низкий"
    MIDDLE = "средний"
    HIGH = "высокий"


class CategoryParameters:
    HOME = "дом"
    WORK = "работа"
    FAMILY = "семья"
    ALL_CATEGORIES = [HOME, WORK, FAMILY]


class TaskParameters:
    TITLE = "Test title of task"
    DESCRIPTION = "Test task description"
    DEADLINE = datetime.now() + timedelta(days=1)
    CATEGORIES = CategoryParameters.ALL_CATEGORIES
    STATUS = StatusParameters.IN_PROGRESS
    PRIORITY = PriorityParameters.HIGH


@dataclass
class Account:
    username: str
    email: str
    password: str
