from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from src.settings.settings import templates

auth_router = APIRouter()

@auth_router.get("/login", response_class=HTMLResponse, name="login")
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.get("/register", response_class=HTMLResponse, name="register")
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
