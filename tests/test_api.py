from fastapi.testclient import TestClient
import app
from app import app as fastapi_app

client = TestClient(fastapi_app)


# 1. Заглушка для успешного ответа от функции get_weather
async def mock_get_weather_success(city, client=None):
    return {
        "city": "Москва",
        "temp": 15.2,
        "description": "небольшая облачность",
        "humidity": 60,
        "pressure": 1013,
        "wind_speed": 4.5,
        "condition": "Clouds"
    }


# 2. Заглушка для сценария, когда город не найден (404)
async def mock_get_weather_not_found(city, client=None):
    return {"error": "Город не найден. Проверьте название."}


def test_weather_success(monkeypatch):
    """Тест успешного получения погоды."""
    monkeypatch.setattr(app, "get_weather", mock_get_weather_success)

    with TestClient(fastapi_app) as client:
        response = client.get("/weather", params={"city": "Moscow"})

        assert response.status_code == 200
        data = response.json()
        assert "error" not in data
        assert data["city"] == "Москва"
        assert data["temp"] == 15.2
        assert data["description"] == "небольшая облачность"
        assert data["wind_speed"] == 4.5
        assert data["condition"] == "Clouds"
        assert data["pressure"] == 1013


def test_weather_unknown_city(monkeypatch):
    """Тест сценария, когда город не найден."""
    monkeypatch.setattr(app, "get_weather", mock_get_weather_not_found)

    with TestClient(fastapi_app) as client:
        response = client.get("/weather", params={"city": "Abcdefg123"})

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "не найден" in data["error"].lower()


def test_weather_invalid_input():
    """Тест проверки невалидного ввода (валидация спецсимволов)."""
    with TestClient(fastapi_app) as client:
        response = client.get("/weather", params={"city": "<script>alert(1)</script>"})

        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert "некорректное название" in data["error"].lower()


def test_history_endpoint():
    """Тест эндпоинт истории."""
    with TestClient(fastapi_app) as client:
        response = client.get("/history", params={"limit": 5})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
