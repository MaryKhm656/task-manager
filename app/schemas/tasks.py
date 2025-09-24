from dataclasses import dataclass
from typing import List, Optional

NOT_PROVIDED = object()


@dataclass
class TaskCreateData:
    title: str
    description: Optional[str] = None
    deadline: Optional[str] = None
    categories: Optional[List[int]] = None
    status: str = "не выполнена"
    priority: str = "средний"


@dataclass
class TaskUpdateData:
    title: Optional[str] = NOT_PROVIDED
    description: Optional[str] = NOT_PROVIDED
    deadline: Optional[str] = NOT_PROVIDED
    categories: Optional[List[int]] = NOT_PROVIDED  # ← Используем sentinel
    status: Optional[str] = NOT_PROVIDED
    priority: Optional[str] = NOT_PROVIDED


@dataclass
class TaskFilterData:
    status: Optional[str] = None
    priority: Optional[str] = None
