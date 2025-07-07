from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from src.settings.settings import templates

pages_router = APIRouter()


@pages_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user_id = request.session.get("user_id")
    return templates.TemplateResponse(
        "home.html", {"request": request, "user_id": str(user_id) if user_id else ""}
    )