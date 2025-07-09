from fastapi import Request, APIRouter, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from src.settings.settings import templates
from src.base.postgres import get_user_stats, get_user_login

profile_router = APIRouter()

@profile_router.get("/profile", response_class=HTMLResponse, name="profile")
async def profile(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    username = await get_user_login(int(user_id))
    return templates.TemplateResponse(
        "profile.html", {"request": request, "username": username or str(user_id)}
    )

@profile_router.get("/friends", response_class=HTMLResponse, name="friends")
async def friends(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("friends.html", {"request": request})


@profile_router.get("/settings", response_class=HTMLResponse, name="settings")
async def settings(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("settings.html", {"request": request})

@profile_router.get("/api/stats")
async def api_stats(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED)
    stats = await get_user_stats(int(user_id))
    return JSONResponse(stats)
