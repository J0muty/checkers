from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from core.settings import templates
from base import postgres
from typing import Union


async def process_login(request: Request) -> Union[HTMLResponse, RedirectResponse]:
    if request.method == "GET":
        return templates.TemplateResponse("login/login.html", {"request": request})

    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    user = await postgres.get_user_by_username(username)
    if not user or user.password != password:
        message = "Неверный логин или пароль"
        return templates.TemplateResponse("login/login.html", {"request": request, "message": message})

    request.session["user"] = username
    return RedirectResponse(url="/", status_code=302)


async def process_registration(request: Request) -> Union[HTMLResponse, RedirectResponse]:
    if request.method == "GET":
        return templates.TemplateResponse("register/register.html", {"request": request})

    form = await request.form()
    username = form.get("username")
    password = form.get("password")

    existing_user = await postgres.get_user_by_username(username)
    if existing_user:
        message = "Пользователь с таким логином уже существует"
        return templates.TemplateResponse("register/register.html", {"request": request, "message": message})

    try:
        await postgres.create_user(username, password)
        return RedirectResponse(url="/login", status_code=302)
    except Exception as e:
        message = f"Ошибка регистрации: {e}"
        return templates.TemplateResponse("register/register.html", {"request": request, "message": message})
