import os
import re
import httpx2 as httpx
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = os.getenv("OWM_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "Ошибка конфигурации: не найден OWM_API_KEY в файле .env. "
        "Добавь строку OWM_API_KEY=твой_ключ в файл .env в корне проекта."
    )


def sanitize_city(city: str) -> str | None:
    """Очищаем и валидируем название города. Возвращает None, если город не валиден"""
    if not city:
        return None
    city = city.strip()
    if not city:
        return None
    if len(city) > 100:
        return None
    if city.isdigit():
        return None
    if not re.match(r"^[\w\s\-'.]+$", city, re.UNICODE):
        return None
    return city


async def get_weather(city: str) -> dict:
    clean_city = sanitize_city(city)
    if clean_city is None:
        return {"error": "Некорректное название города. Используйте только буквы, пробелы и дефисы."}

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

        weather_list = data.get("weather", [])
        if not weather_list:
            return {"error": "Не удалось получить описание погоды."}

        first_weather = weather_list[0]
        description = first_weather.get("description", "Нет данных")
        main_condition = first_weather.get("main", "Unknown")

        main_data = data.get("main", {})
        wind_data = data.get("wind", {})
        return {
            "city": data.get("name", clean_city),
            "temp": main_data.get("temp"),
            "description": description,
            "humidity": main_data.get("humidity"),
            "pressure": main_data.get("pressure"),
            "wind_speed": wind_data.get("speed"),
            "condition": main_condition,
        }

    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        if status_code == 404:
            return {"error": "Город не найден. Проверьте название."}
        elif status_code == 401:
            return {"error": "Неверный API-ключ. Проверьте OWM_API_KEY в .env."}
        else:
            logger.error("HTTP ошибка: %s", status_code)
            return {"error": f"Ошибка сервиса погоды (код {status_code})."}

    except httpx.RequestError as e:
        logger.error(f"Сетевая ошибка: {e}")
        return {"error": f"Не удалось получить данные: {e}"}

    except KeyError as e:
        logger.error(f"Неожиданная структура данных от API: {e}")
        return {"error": "Сервис погоды вернул некорректные данные."}
