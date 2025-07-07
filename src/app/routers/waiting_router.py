from fastapi import Request, APIRouter, status
from fastapi.responses import HTMLResponse, RedirectResponse
from src.settings.settings import templates

waiting_router = APIRouter()

@waiting_router.get("/waiting", response_class=HTMLResponse, name="profile")
async def waiting(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("waiting.html", {"request": request})