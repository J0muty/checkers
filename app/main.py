import uvicorn
import asyncio
import json
from fastapi import FastAPI, Request, HTTPException, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.engine import URL
from base import postgres
from core.settings import templates, static_files
from engine.auth import process_login, process_registration

app = FastAPI()
router = APIRouter()
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
@app.get("/profile/{username}", response_class=HTMLResponse)
async def profile(request: Request, username: str = None):
    if username is None:
        if "user" not in request.session:
            return RedirectResponse(url="/login", status_code=302)
        username = request.session.get("user")
        return RedirectResponse(url=f"/profile/{username}", status_code=302)
    user_profile = await postgres.get_user_by_username(username)
    if user_profile is None:
        return HTMLResponse(content="Пользователь не найден", status_code=404)
    return templates.TemplateResponse("profile/profile.html", {"request": request, "user": user_profile})


@app.get("/waiting", response_class=HTMLResponse)
async def waiting(request: Request):
    waiting_key = request.session.get("waiting_game_key")
    return templates.TemplateResponse("waiting/waiting.html", {"request": request, "waiting_key": waiting_key})


@app.post("/waiting/cancel", response_class=JSONResponse)
async def cancel_waiting(request: Request):
    request.session.pop("waiting_game_key", None)
    return JSONResponse(content={"message": "Поиск отменён"})


@app.get("/board", response_class=HTMLResponse)
async def board(request: Request):
    return templates.TemplateResponse("board/board.html", {"request": request})


app.include_router(router)

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
