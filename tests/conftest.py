import pytest
from db import init_db, get_db_connection


@pytest.fixture(autouse=True)
def setup_db():
    """
    Автоматически инициализирует БД перед началом тестов и
    полностью очищает таблицу погодных данных до и после каждого теста.
    """
    init_db()
    with get_db_connection() as conn:
        conn.execute("DELETE FROM weather")
        conn.commit()

    yield
    # Очищаем таблицу после теста
    with get_db_connection() as conn:
        conn.execute("DELETE FROM weather")
        conn.commit()

@pytest.fixture(autouse=True)
def disable_rate_limit(monkeypatch):
    """
    Полностью отключаем ограничение Rate Limiting на время тестов, чтобы
    запросы от TestClient не блокировались статус-кодом 429.
    """
    try:
        from app import app

        # Проверяем, инициализирован лимитер в приложении
        if hasattr(app.state, "limiter"):
            # Создаем пустой декоратор-пустышку
            def mock_limit( *_args, **_kwargs):
                def decorator(route_function):
                    return route_function
                return decorator

            # Подменяем оригинальный метод limit у SlowApi лимитера
            monkeypatch.setattr(app.state.limiter, "limit", mock_limit)

            # Дополнительно выключаем внутренний флаг лимитера
            setattr(app.state.limiter, "enabled", False)
    except (ImportError, AttributeError):
        pass