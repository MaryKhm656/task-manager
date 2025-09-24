from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union


@dataclass
class TaskCreateData:
    title: str
    description: Optional[str] = None
    deadline: Union[datetime, str] = None
    categories: Optional[List[str]] = None
    status: str = "не выполнена"
    priority: str = "средний"


@dataclass
class TaskUpdateData:
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Union[datetime, str] = None
    categories: Optional[List[int]] = None
    status: Optional[str] = None
    priority: Optional[str] = None


@dataclass
class TaskFilterData:
    status: Optional[str] = None
    priority: Optional[str] = None
