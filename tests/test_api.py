from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient
from app import app

import httpx2 as httpx

client = TestClient(app)


def mock_success_response():
    """Фиктивный успешный ответ от OWM"""
    resp = MagicMock()
    resp.status_code = 200
    resp.raise_for_status.return_value = None
    resp.json.return_value = {
        "name": "Moscow",
        "main": {
            "temp": 15.2,
            "humidity": 60,
            "pressure": 1013
        },
        "wind": {"speed": 4.5},
        "weather": [
            {"description": "небольшая облачность", "main": "Clouds"}
        ]
    }
    return resp


def mock_not_found_response():
    """Фиктивный ответ 404 — город не найден."""
    resp = MagicMock()
    resp.status_code = 404
    http_err = httpx.HTTPStatusError("Not Found", request=MagicMock(), response=resp)
    resp.raise_for_status.side_effect = http_err
    resp.json.return_value = {"message": "Город не найден"}
    return resp


@patch("api.httpx.AsyncClient")
def test_weather_success(mock_client_cls):
    """Реальный город должен возвращать погоду (мок)."""
    mock_client = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_client
    mock_client.get = AsyncMock(return_value=mock_success_response())

    response = client.get("/weather", params={"city": "Moscow"})
    assert response.status_code == 200
    data = response.json()
    assert "error" not in data
    assert data["city"] == "Moscow"
    assert data["temp"] == 15.2
    assert data["description"] == "небольшая облачность"
    assert data["wind_speed"] == 4.5
    assert data["condition"] == "Clouds"
    assert data["pressure"] == 1013


@patch("api.httpx.AsyncClient")
def test_weather_unknown_city(mock_client_cls):
    """Несуществующий город должен вернуть ошибку (мок)."""
    mock_client = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_client
    mock_client.get = AsyncMock(return_value=mock_not_found_response())

    response = client.get("/weather", params={"city": "Abcdefg123"})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "не найден" in data["error"].lower()


@patch("api.httpx.AsyncClient")
def test_weather_invalid_input(mock_client_cls):
    """Невалидный город (спецсимволы) должен вернуть ошибку без запроса к API."""
    mock_client = AsyncMock()
    mock_client_cls.return_value.__aenter__.return_value = mock_client
    mock_client.get = AsyncMock()

    response = client.get("/weather", params={"city": "<script>alert(1)</script>"})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    mock_client.get.assert_not_called()


def test_history_endpoint():
    """История должна возвращать список."""
    response = client.get("/history", params={"limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "city" in data[0]
        assert "temp" in data[0]
