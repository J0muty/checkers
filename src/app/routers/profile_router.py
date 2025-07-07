from fastapi import Request, APIRouter, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from src.settings.settings import templates
from src.base.postgres import get_user_stats

profile_router = APIRouter()

@profile_router.get("/profile", response_class=HTMLResponse, name="profile")
async def profile(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("profile.html", {"request": request, "user_id": user_id})

@profile_router.get("/api/stats")
async def api_stats(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return JSONResponse({"error": "unauthorized"}, status_code=status.HTTP_401_UNAUTHORIZED)
    stats = await get_user_stats(int(user_id))
    return JSONResponse(stats)
