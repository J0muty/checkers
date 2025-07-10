import json
from fastapi import Request, APIRouter, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from src.settings.settings import templates
from src.base.postgres import (
    get_user_stats,
    get_user_login,
    get_friends,
    get_friend_requests,
    search_users,
    send_friend_request,
    cancel_friend_request,
    remove_friend,
)
from src.app.routers.ws_router import friends_manager

profile_router = APIRouter()

@profile_router.get("/profile", response_class=HTMLResponse, name="profile")
async def profile(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    username = await get_user_login(int(user_id))
    return templates.TemplateResponse("profile.html", {"request": request, "username": username or str(user_id)})

@profile_router.get("/profile/friends", response_class=HTMLResponse, name="friends")
async def friends(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "friends.html", {"request": request, "user_id": str(user_id)}
    )


@profile_router.get("/api/friends")
async def api_friends(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED)
    uid = int(user_id)
    friends = await get_friends(uid)
    requests = await get_friend_requests(uid)
    return JSONResponse({"friends": friends, "requests": requests})

@profile_router.get("/api/search_users")
async def api_search_users(request: Request, q: str):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED)
    uid = int(user_id)
    users = await search_users(q, uid)
    return JSONResponse({"users": users})

@profile_router.post("/api/friend_request")
async def api_friend_request(request: Request, to_id: int, action: str = "send"):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    uid = int(user_id)
    if action == "send":
        await send_friend_request(uid, to_id)
    elif action == "cancel":
        await cancel_friend_request(uid, to_id)
    elif action == "accept":
        await send_friend_request(uid, to_id)
    elif action == "reject":
        await cancel_friend_request(to_id, uid)
    elif action == "remove":
        await remove_friend(uid, to_id)
    else:
        return JSONResponse({"error": "unknown action"}, status_code=400)
    msg = json.dumps({"action": "update"})
    await friends_manager.broadcast(str(uid), msg)
    await friends_manager.broadcast(str(to_id), msg)
    return JSONResponse({"status": "ok"})

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
    uid = int(user_id)
    stats = await get_user_stats(uid)
    return JSONResponse(stats)
