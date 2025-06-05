from fastapi import APIRouter, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from src.settings.settings import templates
from src.base.postgres import create_user, authenticate_user

auth_router = APIRouter()

@auth_router.get("/login", response_class=HTMLResponse, name="login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.post("/login", response_class=HTMLResponse, name="login_post")
async def process_login(
    request: Request,
    login: str = Form(...),
    password: str = Form(...),
):
    user = None
    try:
        user = await authenticate_user(login, password)
    except Exception as e:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Внутренняя ошибка при проверке пользователя. Попробуйте позже.",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if not user:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Неправильный логин или пароль.",
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    request.session["user_id"] = user.id

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return response


@auth_router.get("/register", response_class=HTMLResponse, name="register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@auth_router.post("/register", response_class=HTMLResponse, name="register_post")
async def process_register(
    request: Request,
    login: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
):
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Пароли не совпадают.",
                "login": login,
                "email": email,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    try:
        user = await create_user(login=login, email=email, password=password)
    except ValueError as ve:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": str(ve),
                "login": login,
                "email": email,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        return templates.TemplateResponse(
            "register.html",
            {
                "request": request,
                "error": "Внутренняя ошибка при создании пользователя. Попробуйте позже.",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    request.session["user_id"] = user.id

    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    return response

@auth_router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/", status_code=status.HTTP_302_FOUND)