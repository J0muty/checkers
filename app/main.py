import uuid
import json
import asyncio
import uvicorn
from fastapi import FastAPI, Request, APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from core.settings import templates, static_files
from base import postgres
from base.redis import (
    redis_client,
    create_or_join_waiting,
    cancel_waiting_in_redis,
    active_waiting_connections,
    notify_game_found,
    remove_game_in_redis
)
from engine.auth import process_login, process_registration
from engine.game import pieces

app = FastAPI()
router = APIRouter()

app.mount("/static", static_files, name="static")
app.add_middleware(SessionMiddleware, secret_key="secretkey")


@app.on_event("startup")
async def startup_event():
    await postgres.init_db()


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

    return templates.TemplateResponse("profile/profile.html", {
        "request": request,
        "user": user_profile
    })


@app.get("/waiting", response_class=HTMLResponse)
async def waiting(request: Request):
    waiting_key = request.session.get("waiting_game_key")
    return templates.TemplateResponse("waiting/waiting.html", {
        "request": request,
        "waiting_key": waiting_key
    })


@app.post("/waiting/cancel", response_class=JSONResponse)
async def cancel_waiting(request: Request):
    waiting_key = request.session.get("waiting_game_key")
    if waiting_key:
        await cancel_waiting_in_redis(waiting_key)
        request.session.pop("waiting_game_key", None)
    return JSONResponse(content={"message": "Поиск отменён"})


@app.get("/board/{username}/{game_id}", response_class=HTMLResponse)
async def board_game(request: Request, username: str, game_id: str):
    user = request.session.get("user")
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    game_key = f"game:{game_id}"
    game_data = await redis_client.hgetall(game_key)
    if not game_data:
        return HTMLResponse("Игра не найдена", status_code=404)
    user1 = game_data.get("user1")
    user2 = game_data.get("user2")
    if user not in (user1, user2):
        return HTMLResponse("Нет доступа к игре", status_code=403)
    if username != user:
        return HTMLResponse("Нет доступа к игре", status_code=403)
    pieces_json = game_data.get("pieces")
    if pieces_json:
        current_pieces = json.loads(pieces_json)
    else:
        from engine.game import pieces
        current_pieces = pieces

    request.session["game_id"] = game_id

    return templates.TemplateResponse("board/board.html", {
        "request": request,
        "pieces": current_pieces
    })


@app.post("/game/search")
async def search_game(request: Request):
    user = request.session.get("user")
    if not user:
        return JSONResponse({"error": "Not authenticated."}, status_code=401)

    waiting_game_id, game_id, user1 = await create_or_join_waiting(user)
    if game_id is not None:
        request.session["game_id"] = game_id
        await notify_game_found(waiting_game_id, user1, game_id)
        return JSONResponse({"redirect": f"/board/{user}/{game_id}"})
    else:
        request.session["waiting_game_key"] = waiting_game_id
        return JSONResponse({"redirect": "/waiting"})


@app.websocket("/ws/game")
async def websocket_game(websocket: WebSocket):
    game_key = websocket.query_params.get("game_key")
    await websocket.accept()

    if not game_key:
        await websocket.close()
        return
    active_waiting_connections[game_key] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if game_key in active_waiting_connections:
            del active_waiting_connections[game_key]


@app.post("/give_up")
async def give_up(request: Request):
    game_id = request.session.get("game_id")
    if game_id:
        await remove_game_in_redis(game_id)
        request.session.pop("game_id", None)
    return JSONResponse({"message": "Game gave up"})


app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=1488, reload=True)
