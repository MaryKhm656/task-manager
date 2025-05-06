from fastapi import APIRouter, HTTPException, Depends, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.schemas import User, UserRead, UserCreate, Category, CategoryCreate, CategoryOut, CategoryTitleOnly, Task, TaskCreate, TaskRead
import app.crud.functions as fn
from app.crud.auth import get_current_user, admin_required, login_user
from app.db import models
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Optional
from datetime import datetime

router = APIRouter(prefix="/api")

@router.post("/register", response_model=UserRead)
def create_user(user: UserCreate):
    try:
        created = fn.create_user(
            name=user.name,
            email=user.email,
            password=user.password
        )
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        token = login_user(email=form_data.username, password=form_data.password)
        return {"access_token": token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.post("/tasks", response_model=TaskRead)
def create_task(
        task: TaskCreate,
        current_user: models.User = Depends(get_current_user)
):
    try:
        created = fn.create_task(
            user_id=current_user.id,
            title=task.title,
            description=task.description,
            deadline=task.deadline,
            categories=task.categories,
            status=task.status,
            priority=task.priority
        )
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.post("/categories", response_model=CategoryOut)
def create_category(category: CategoryCreate, current_user: models.User = Depends(admin_required)):
    try:
        created = fn.create_category(
            title=category.title
        )
        return created
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.get("/tasks/all", response_model=List[TaskRead])
def get_all_tasks_user(current_user: models.User = Depends(get_current_user)):
    try:
        tasks = fn.get_all_user_tasks(user_id=current_user.id)
        return tasks
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.get("/tasks", response_model=List[TaskRead])
def get_tasks_by_filters(
        status: Optional[str] = Query(None, description="Статус задачи"),
        priority: Optional[str] = Query(None, description="Приоритет задачи"),
        current_user: models.User = Depends(get_current_user)
    ):
    try:
        tasks = fn.get_filtered_tasks(
            user_id=current_user.id,
            status=status,
            priority=priority
        )
        return tasks
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
@router.get("/categories", response_model=List[CategoryTitleOnly])
def get_all_categories():
    try:
        all_categories = fn.get_all_categories()
        return all_categories
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.put("/tasks/{task_id}/status", response_model=TaskRead)
def update_task_status(task_id: int, new_status: str, current_user: models.User = Depends(get_current_user)):
    try:
        updated_task = fn.update_task_status(
            user_id=current_user.id,
            task_id=task_id,
            new_status=new_status
        )
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.put("/tasks/{task_id}/priority", response_model=TaskRead)
def update_task_priority(task_id: int, new_priority: str, current_user: models.User = Depends(get_current_user)):
    try:
        updated_task = fn.update_task_priority(
            user_id=current_user.id,
            task_id=task_id,
            new_priority=new_priority
        )
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.put("/tasks/{task_id}/deadline", response_model=TaskRead)
def update_task_deadline(task_id: int, new_deadline: str | datetime, current_user: models.User = Depends(get_current_user)):
    try:
        updated_task = fn.update_deadline(
            user_id=current_user.id,
            task_id=task_id,
            new_deadline=new_deadline
        )
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.put("/tasks/{task_id}/description", response_model=TaskRead)
def update_task_description(task_id: int, new_description: str, current_user: models.User = Depends(get_current_user)):
    try:
        updated_task = fn.update_description(
            user_id=current_user.id,
            task_id=task_id,
            new_description=new_description
        )
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")


@router.put("/tasks/{task_id}/categories", response_model=TaskRead)
def update_task_categories(
        task_id: int,
        new_categories: List[str] = Query(..., description="Список категорий"),
        current_user: models.User = Depends(get_current_user)
):
    try:
        updated_task = fn.update_task_categories(
            user_id=current_user.id,
            task_id=task_id,
            new_categories=new_categories
        )
        return updated_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.delete("/users")
def delete_user(current_user: models.User = Depends(get_current_user)):
    try:
        message = fn.delete_user(user_id=current_user.id)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")
    
    
@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: models.User = Depends(get_current_user)):
    try:
        message = fn.delete_task(
            user_id=current_user.id,
            task_id=task_id
        )
        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, current_user: models.User = Depends(admin_required)):
    try:
        message = fn.delete_category(category_id=category_id)
        return {"message": message}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Ошибка при работе с базой данных")