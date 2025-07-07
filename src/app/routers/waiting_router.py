from fastapi import Request, APIRouter, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from src.settings.settings import templates
from src.base.redis import add_to_waiting, check_waiting, cancel_waiting

waiting_router = APIRouter()

@waiting_router.get("/waiting", response_class=HTMLResponse, name="waiting")
async def waiting(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse(
        "waiting.html",
        {"request": request, "user_id": str(user_id)},
    )


@waiting_router.post("/api/search_game")
async def api_search_game(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401)
    board_id, color = await add_to_waiting(str(user_id))
    return JSONResponse({"board_id": board_id, "color": color})


@waiting_router.get("/api/check_game")
async def api_check_game(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401)
    board_id, color = await check_waiting(str(user_id))
    return JSONResponse({"board_id": board_id, "color": color})


@waiting_router.post("/api/cancel_game")
async def api_cancel_game(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401)
    await cancel_waiting(str(user_id))
    return JSONResponse({"status": "ok"})