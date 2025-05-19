from fastapi import Request, APIRouter
from fastapi.responses import HTMLResponse
from src.settings.settings import templates

pages_router = APIRouter()


@pages_router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})