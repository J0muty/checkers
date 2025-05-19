from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from src.app.routers import pages_router, auth_router
from src.settings.settings import static_files

@asynccontextmanager
async def lifespan(_app: FastAPI):


    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="absolutesecretkey")
app.include_router(pages_router)
app.include_router(auth_router)
app.mount("/static", static_files, name="static")


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=1337)