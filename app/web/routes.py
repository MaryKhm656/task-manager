from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette.status import HTTP_302_FOUND

from app.crud import functions as fn
from app.crud.auth import get_current_user_from_cookie, login_user
from app.crud.constants import ALLOWED_PRIORITIES, ALLOWED_STATUSES
from app.db.models import User
from app.dependencies import get_db
from app.schemas.tasks import TaskCreateData, TaskUpdateData
from app.services.category_service import CategoryService
from app.services.task_service import TaskService
from app.services.user_service import UserService

templates = Jinja2Templates(directory="templates")

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def reed_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class=HTMLResponse)
async def register_form_submit(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        UserService.create_user(
            db, name, email, password
        )

        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)

    except ValidationError as e:
        error_msgs = [f"{err['loc'][0]}: {err['msg']}" for err in e.errors()]
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": " | ".join(error_msgs)},
            status_code=400,
        )

    except ValueError as e:
        return templates.TemplateResponse(
            "register.html", {"request": request, "error": str(e)}
        )

    except SQLAlchemyError:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Ошибка при работе с базой данных"},
            status_code=500,
        )


@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_class=HTMLResponse)
async def login_form_submit(
    request: Request, email: str = Form(...), password: str = Form(...)
):
    try:
        access_token = login_user(email, password)

        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(key="access_token", value=access_token, httponly=True)
        return response
    except ValueError as e:
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": str(e)}, status_code=400
        )
    except SQLAlchemyError:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Ошибка при работе с базой данных"},
            status_code=500,
        )


@router.get("/dashboard", response_class=HTMLResponse)
async def get_user_account(
    request: Request, current_user: User = Depends(get_current_user_from_cookie)
):
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user_name": current_user.name,
            "is_admin": current_user.is_admin,
        },
    )


@router.post("/dashboard", response_class=HTMLResponse)
async def post_del_user(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    try:
        UserService.delete_user(db, current_user.id)
        response = RedirectResponse(
            url="/delete-account-success", status_code=HTTP_302_FOUND
        )
        response.delete_cookie("access_token")
        return response
    except ValueError as e:
        return templates.TemplateResponse(
            "dashboard.html",
            {"request": request, "user_name": current_user.name, "error": str(e)},
        )


@router.get("/delete-account-success", response_class=HTMLResponse)
async def delete_account(request: Request):
    return templates.TemplateResponse(
        "delete-account-success.html", {"request": request}
    )


@router.get("/create-task", response_class=HTMLResponse)
async def get_create_task(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    categories=None,
):
    if categories is None:
        categories = CategoryService.get_all_categories(get_db())
    return templates.TemplateResponse(
        "create-task.html", {"request": request, "categories": categories}
    )


@router.post("/create-task", response_class=HTMLResponse)
async def post_create_task(
    request: Request,
    task_data: TaskCreateData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    try:
        if task_data.deadline:
            task_data.deadline = task_data.deadline.replace("T", " ")

        TaskService.create_task(
            db=db, user_id=current_user.id, task_data=task_data
        )

        return RedirectResponse(
            url="/task-creation-success", status_code=HTTP_302_FOUND
        )

    except ValueError as e:
        categories_list = CategoryService.get_all_categories(db)
        return templates.TemplateResponse(
            "create-task.html",
            {"request": request, "categories": categories_list, "error": str(e)},
        )


@router.get("/task-creation-success", response_class=HTMLResponse)
async def get_success(
    request: Request, current_user: User = Depends(get_current_user_from_cookie)
):
    return templates.TemplateResponse(
        "task-creation-success.html", {"request": request}
    )


@router.get("/tasks", response_class=HTMLResponse)
async def get_all_tasks_user(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    tasks = TaskService.get_all_user_tasks(db, current_user.id)
    return templates.TemplateResponse(
        "tasks.html",
        {"request": request, "tasks": tasks, "user_name": current_user.name},
    )


@router.post("/tasks/{task_id}", response_class=HTMLResponse)
async def delete_task(
    request: Request,
    task_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    try:
        TaskService.delete_task(db, current_user.id, task_id)
        tasks = TaskService.get_all_user_tasks(db=db, user_id=current_user.id)
        return templates.TemplateResponse(
            "tasks.html",
            {
                "request": request,
                "tasks": tasks,
                "user_name": current_user.name,
                "success": True,
            },
        )
    except ValueError as e:
        tasks = TaskService.get_all_user_tasks(db=db, user_id=current_user.id)
        return templates.TemplateResponse(
            "tasks.html",
            {
                "request": request,
                "tasks": tasks,
                "user_name": current_user.name,
                "error": str(e),
            },
        )


@router.get("/edit-task/{task_id}", response_class=HTMLResponse)
async def get_task_by_id(
    request: Request,
    task_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db),
    categories=None,
):
    if categories is None:
        categories = CategoryService.get_all_categories(db)
    task_by_id = TaskService.get_user_task_by_id(db=db, user_id=current_user.id, task_id=task_id)
    return templates.TemplateResponse(
        "edit-task.html",
        {
            "request": request,
            "task": task_by_id,
            "categories": categories,
            "allowed_statuses": ALLOWED_STATUSES,
            "allowed_priorities": ALLOWED_PRIORITIES,
        },
    )


@router.post("/edit-task/{task_id}", response_class=HTMLResponse)
async def post_edit_task(
    request: Request,
    task_id: int,
    update_data = TaskUpdateData,
    current_user: User = Depends(get_current_user_from_cookie),
        db: Session = Depends(get_db)
):
    try:
        if update_data.deadline:
            update_data.deadline = update_data.deadline.replace("T", " ")

        updated_task = TaskService.update_task_full(db=db, user_id=current_user.id, task_id=task_id, update_data=update_data)

        all_categories = CategoryService.get_all_categories(db)
        return templates.TemplateResponse(
            "edit-task.html",
            {
                "request": request,
                "task": updated_task,
                "categories": all_categories,
                "allowed_statuses": ALLOWED_STATUSES,
                "allowed_priorities": ALLOWED_PRIORITIES,
                "success": True,
            },
        )

    except ValueError as e:
        all_categories = CategoryService.get_all_categories(db)
        task = TaskService.get_user_task_by_id(db=db, user_id=current_user.id, task_id=task_id)
        return templates.TemplateResponse(
            "edit-task.html",
            {
                "request": request,
                "task": task,
                "categories": all_categories,
                "allowed_statuses": ALLOWED_STATUSES,
                "allowed_priorities": ALLOWED_PRIORITIES,
                "error": str(e),
            },
        )


@router.get("/edit-categories", response_class=HTMLResponse)
async def get_edit_categories(
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    error: Optional[str] = None,
    success: Optional[str] = None,
    db: Session = Depends(get_db)
):
    all_categories = CategoryService.get_all_categories(db)
    return templates.TemplateResponse(
        "edit-categories.html",
        {
            "request": request,
            "categories": all_categories,
            "is_admin": current_user.is_admin,
            "error": error,
            "success": success == "True",
        },
    )


@router.post("/add-categories", response_class=HTMLResponse)
async def post_add_category(
    request: Request,
    title: str = Form(...),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    try:
        if not current_user.is_admin:
            raise ValueError("Доступ запрещен")
        CategoryService.create_category(db=db, title=title)

        return RedirectResponse("/edit-categories?success=True", status_code=302)
    except ValueError as e:
        return RedirectResponse(f"/edit-categories?error={str(e)}", status_code=400)


@router.post("/delete-categories", response_class=HTMLResponse)
async def post_del_category(
    request: Request,
    categories: list[int] = Form(...),
    current_user: User = Depends(get_current_user_from_cookie),
    db: Session = Depends(get_db)
):
    try:
        if not current_user.is_admin:
            raise ValueError("Доступ запрещен")
        CategoryService.delete_categories_list(db, categories)
        return RedirectResponse("/edit-categories?success=True", status_code=302)
    except ValueError as e:
        return RedirectResponse(f"/edit-categories?error={str(e)}", status_code=400)
