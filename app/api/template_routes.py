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
