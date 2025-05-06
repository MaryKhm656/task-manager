from pydantic import BaseModel, EmailStr, constr, Field
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    name: constr(min_length=2, max_length=100) = Field(..., description="Имя пользователя")
    email: EmailStr = Field(..., description="Электронная почта в формате user@mail.com")
    password: constr(min_length=4, max_length=256) = Field(..., description="Придумайте пароль длиной от 4 до 20 символов")
    
    
class UserLogin(BaseModel):
    email: EmailStr
    password: constr(min_length=4, max_length=20)
    
    
class UserCreate(User):
    pass

class UserRead(User):
    id: int
    
    class Config:
        from_attributes = True


class Category(BaseModel):
    title: constr(min_length=1, max_length=50) = Field(..., description="Название категории")

class CategoryCreate(Category):
    pass

class CategoryOut(Category):
    id: int

    class Config:
        from_attributes = True


class CategoryTitleOnly(Category):
    pass

class Task(BaseModel):
    title: constr(max_length=100) = Field(..., description="Название задачи")
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[str] = "не выполнена"
    priority: Optional[str] = "средний"
    categories: Optional[List[str]] = None
    
class TaskCreate(Task):
    pass

class TaskRead(Task):
    id: int
    categories: Optional[List[CategoryTitleOnly]] = None
    
    class Config:
        from_attributes = True
    
    

