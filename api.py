import os
import re
import requests
from dotenv import load_dotenv
import logging

# Настройка логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Загружаем переменные из .env
load_dotenv()

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = os.getenv("OWM_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "Ошибка конфигурации: не найден OWM_API_KEY в файле .env. "
        "Добавь строку OWM_API_KEY=твой_ключ в файл .env в корне проекта."
    )


def sanitize_city(city: str) -> str | None:
    """Очищаем и валидируем название города. Возращает None, если город не валиден"""
    if not city:
        return None
    # Убираем пробелы по краям
    city = city.strip()

    # Пустая строка после обрезки
    if not city:
        return None

    # Слишком длинное название
    if len(city) > 100:
        return None

    # Только цифры
    if city.isdigit():
        return None
    # Разрешаем буквы (любые алфавиты), пробелы, дефисы, апострофы и точки. Запрещаем спецсимволы
    if not re.match(r"^[\w\s\-'.]+$", city, re.UNICODE):
        return None
    return city


def get_weather(city: str) -> dict:
    # Валидация входных данных
    clean_city = sanitize_city(city)
    if clean_city is None:
        return {"error": "Некорректное название города. Используйте только буквы, пробелы и дефисы."}

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
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
            "condition": main_condition
        }


    except requests.exceptions.HTTPError:
        status_code = response.status_code
        if status_code == 404:
            return {"error": "Город не найден. Проверьте название."}
        elif status_code == 401:
            return {"error": "Неверный API-ключ. Проверьте OWM_API_KEY в .env."}
        else:
            logger.error("HTTP ошибка: %s", status_code)
            return {"error": f"Ошибка сервиса погоды (код {status_code})."}


    except requests.exceptions.RequestException as e:
        logger.error(f"Сетевая ошибка: {e}")
        return {"error": f"Не удалось получить данные: {e}"}

    except KeyError as e:
        logger.error(f"Неожиданная структура данных от API: {e}")
        return {"error": "Сервис погоды вернул некорректные данные."}
