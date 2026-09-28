import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx2 as httpx
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from api import get_weather
from db import save_weather, get_history, init_db


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    # Безопасно инициализируем бд в пуле потоков при старте
    await run_in_threadpool(init_db)

    # Создаем единый асинхронный клиент для работы с внешним API
    async with httpx.AsyncClient() as client:
        fastapi_app.state.http_client = client
        yield


app = FastAPI(lifespan=lifespan)

# Настройка ограничений частоты запросов
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(_request: Request, _exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"error": "Слишком много запросов. Попробуйте позже."},
    )


# Подключение статики и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

HOST = os.getenv("APP_HOST", "127.0.0.1")
PORT = int(os.getenv("APP_PORT", "8000"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})


@app.get("/weather")
@limiter.limit("10/minute")
async def weather(request: Request, city: str = "Krasnodar"):
    result = await get_weather(city, client=request.app.state.http_client)

    if "error" in result:
        return result

    await run_in_threadpool(save_weather, result)
    return result


@app.get("/history")
async def history(limit: int = 10):
    data = await run_in_threadpool(get_history, limit)
    return data


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host=HOST, port=PORT, reload=True)
