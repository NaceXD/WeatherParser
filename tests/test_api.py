from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_weather_success():
    """Реальный город должен возвращать погоду."""
    response = client.get("/weather", params={"city": "Moscow"})
    assert response.status_code == 200
    data = response.json()
    assert "error" not in data
    assert "temp" in data
    assert "description" in data
    assert "city" in data
    assert "wind_speed" in data
    assert "condition" in data
    assert "pressure" in data


def test_weather_unknown_city():
    """Несуществующий город должен вернуть ошибку."""
    response = client.get("/weather", params={"city": "Abcdefg123"})
    assert response.status_code == 200
    data = response.json()
    assert "error" in data
    assert "не найден" in data["error"].lower()


def test_history_endpoint():
    """История должна возвращать список."""
    response = client.get("/history", params={"limit": 5})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        assert "city" in data[0]
        assert "temp" in data[0]
        assert "wind_speed" in data[0]
        assert "condition" in data[0]
