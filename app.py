import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api import get_weather
from db import save_weather, get_history

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request, "index.html", {})

@app.get("/weather")
async def weather(city: str = "Krasnodar"):
    result = get_weather(city)

    if "error" in result:
        return result

    save_weather(result)
    return result

@app.get("/history")
async def history(limit: int = 10):
    return get_history(limit)


if __name__ == "__main__":
    import uvicorn
    # Запускаем без reload=True внутри скрипта, используем команду uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)