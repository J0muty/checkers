from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
from src.app.routers import pages_router

@asynccontextmanager
async def lifespan(_app: FastAPI):


    yield

app = FastAPI(lifespan=lifespan)

app.include_router(pages_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=1337)