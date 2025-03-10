import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.engine import URL
import asyncio

from base import postgres
from core.settings import templates, static_files
from engine.auth import process_login, process_registration

app = FastAPI()
app.mount("/static", static_files, name="static")
app.add_middleware(SessionMiddleware, secret_key="secretkey")


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = request.session.get("user")
    return templates.TemplateResponse("home/home.html", {"request": request, "user": user})


@app.api_route("/register", methods=["GET", "POST"], response_class=HTMLResponse)
async def register(request: Request):
    return await process_registration(request)


@app.api_route("/login", methods=["GET", "POST"], response_class=HTMLResponse)
async def login(request: Request):
    return await process_login(request)


@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse(url="/", status_code=302)


@app.get("/profile", response_class=HTMLResponse)
async def profile(request: Request):
    if "user" not in request.session:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("profile/profile.html", {"request": request})


if __name__ == "__main__":
    DATABASE_URL = URL.create(
        "postgresql+asyncpg",
        username="postgres",
        password="951753aA.",
        host="localhost",
        database="postgres",
        port=5432
    )
    asyncio.run(postgres.async_main(DATABASE_URL))
    uvicorn.run("main:app", host="127.0.0.1", port=1488)
