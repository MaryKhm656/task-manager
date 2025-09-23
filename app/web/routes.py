from typing import Optional

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.status import HTTP_302_FOUND

from app.crud import functions as fn
from app.crud.auth import get_current_user_from_cookie, login_user
from app.crud.constants import ALLOWED_PRIORITIES, ALLOWED_STATUSES
from app.db.models import User

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
):
    try:
        fn.create_user(name=name, email=email, password=password)

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
    request: Request, current_user: User = Depends(get_current_user_from_cookie)
):
    try:
        fn.delete_user(user_id=current_user.id)
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
    categories=fn.get_all_categories(),
):
    return templates.TemplateResponse(
        "create-task.html", {"request": request, "categories": categories}
    )


@router.post("/create-task", response_class=HTMLResponse)
async def post_create_task(
    request: Request,
    title: str = Form(...),
    description: str = Form(None),
    deadline: str = Form(None),
    status: str = Form(...),
    priority: str = Form(...),
    categories: list[str] = Form(None),
    current_user: User = Depends(get_current_user_from_cookie),
):
    try:
        if deadline:
            deadline = deadline.replace("T", " ")

        fn.create_task(
            user_id=current_user.id,
            title=title,
            description=description,
            deadline=deadline,
            categories=categories,
            status=status,
            priority=priority,
        )

        return RedirectResponse(
            url="/task-creation-success", status_code=HTTP_302_FOUND
        )

    except ValueError as e:
        categories_list = fn.get_all_categories()
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
    request: Request, current_user: User = Depends(get_current_user_from_cookie)
):
    tasks = fn.get_all_user_tasks(user_id=current_user.id)
    return templates.TemplateResponse(
        "tasks.html",
        {"request": request, "tasks": tasks, "user_name": current_user.name},
    )


@router.post("/tasks/{task_id}", response_class=HTMLResponse)
async def delete_task(
    request: Request,
    task_id: int,
    current_user: User = Depends(get_current_user_from_cookie),
):
    try:
        fn.delete_task(user_id=current_user.id, task_id=task_id)
        tasks = fn.get_all_user_tasks(user_id=current_user.id)
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
        tasks = fn.get_all_user_tasks(user_id=current_user.id)
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
    categories=fn.get_all_categories(),
):
    task_by_id = fn.get_user_task_by_id(user_id=current_user.id, task_id=task_id)
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
    title: str = Form(...),
    description: str = Form(None),
    deadline: str = Form(None),
    status: str = Form(...),
    priority: str = Form(...),
    categories: list[str] = Form(None),
    current_user: User = Depends(get_current_user_from_cookie),
):
    try:
        if deadline:
            deadline = deadline.replace("T", " ")

        updated_task = fn.update_task_full(
            user_id=current_user.id,
            task_id=task_id,
            title=title,
            status=status,
            priority=priority,
            deadline=deadline,
            description=description,
            categories=categories,
        )

        all_categories = fn.get_all_categories()
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
        all_categories = fn.get_all_categories()
        task = fn.get_user_task_by_id(user_id=current_user.id, task_id=task_id)
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
):
    all_categories = fn.get_all_categories()
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
):
    try:
        if not current_user.is_admin:
            raise ValueError("Доступ запрещен")
        fn.create_category(title=title)

        return RedirectResponse("/edit-categories?success=True", status_code=302)
    except ValueError as e:
        return RedirectResponse(f"/edit-categories?error={str(e)}", status_code=400)


@router.post("/delete-categories", response_class=HTMLResponse)
async def post_del_category(
    request: Request,
    categories: list[int] = Form(...),
    current_user: User = Depends(get_current_user_from_cookie),
):
    try:
        if not current_user.is_admin:
            raise ValueError("Доступ запрещен")
        fn.delete_categories_list(categories)
        return RedirectResponse("/edit-categories?success=True", status_code=302)
    except ValueError as e:
        return RedirectResponse(f"/edit-categories?error={str(e)}", status_code=400)
