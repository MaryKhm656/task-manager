from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.status import HTTP_302_FOUND
from sqlalchemy.exc import SQLAlchemyError
from app.crud import functions as fn
from app.api.schemas import UserCreate
from app.db.models import User
from app.crud.auth import login_user, get_current_user_from_cookie

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
        password: str = Form(...)
):
    user_data = UserCreate(name=name, email=email, password=password)
    try:
        fn.create_user(
            name=user_data.name,
            email=user_data.email,
            password=user_data.password
        )

        return RedirectResponse(url="/login", status_code=HTTP_302_FOUND)

    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {'request': request, 'error': str(e)},
            status_code=400
        )
    except SQLAlchemyError:
        return templates.TemplateResponse(
            "register.html",
            {'request': request, 'error': "Ошибка при работе с базой данных"},
            status_code=500
        )
    
    
@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {'request': request})

@router.post("/login", response_class=HTMLResponse)
async def login_form_submit(
        request: Request,
        email: str = Form(...),
        password: str = Form(...)
):
    try:
        access_token = login_user(email, password)
        
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True
        )
        return response
    except ValueError as e:
        return templates.TemplateResponse(
            "register.html",
            {'request': request, 'error': str(e)},
            status_code=400
        )
    except SQLAlchemyError:
        return templates.TemplateResponse(
            "register.html",
            {'request': request, 'error': "Ошибка при работе с базой данных"},
            status_code=500
        )

@router.get("/dashboard", response_class=HTMLResponse)
async def get_user_account(request: Request, current_user: User = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse("dashboard.html", {"request": request, "user_name": current_user.name, "is_admin": current_user.is_admin})

@router.get("/create-task", response_class=HTMLResponse)
async def get_create_task(
        request: Request,
        current_user: User = Depends(get_current_user_from_cookie),
        categories = fn.get_all_categories()
):
    return templates.TemplateResponse("create-task.html", {"request": request, "categories": categories})

@router.post("/create-task", response_class=HTMLResponse)
async def post_create_task(
        request: Request,
        title: str = Form(...),
        description: str = Form(None),
        deadline: str = Form(None),
        status: str = Form(...),
        priority: str = Form(...),
        categories: list[str] = Form(None),
        current_user: User = Depends(get_current_user_from_cookie)
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
                priority=priority
            )
            
            return RedirectResponse(url="/task-creation-success", status_code=HTTP_302_FOUND)
        
    except ValueError as e:
        categories_list = fn.get_all_categories()
        return templates.TemplateResponse(
            "create-task.html",
            {
                "request": request,
                "categories": categories_list,
                "error": str(e)
            }
        )
    
    
@router.get("/task-creation-success", response_class=HTMLResponse)
async def get_success(request: Request, current_user: User = Depends(get_current_user_from_cookie)):
    return templates.TemplateResponse("task-creation-success.html", {"request": request})


@router.get("/tasks", response_class=HTMLResponse)
async def get_all_tasks_user(request: Request, current_user: User = Depends(get_current_user_from_cookie)):
    tasks = fn.get_all_user_tasks(user_id=current_user.id)
    return templates.TemplateResponse(
        "tasks.html",
        {
            "request": request,
            "tasks": tasks,
            "user_name": current_user.name
        }
    )

@router.get("/edit-task/{task_id}", response_class=HTMLResponse)
async def get_task_by_id(request: Request, 
                         task_id: int, 
                         current_user: User = Depends(get_current_user_from_cookie),
                         categories = fn.get_all_categories()):
    task_by_id = fn.get_user_task_by_id(user_id=current_user.id, task_id=task_id)
    return templates.TemplateResponse(
        "edit-task.html",
        {
            "request": request,
            "task": task_by_id,
            "categories": categories
        }
    )