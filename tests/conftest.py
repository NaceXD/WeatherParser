import pytest
from db import init_db, get_connection, release_connection


@pytest.fixture(autouse=True)
def setup_db():
    init_db()

    conn = get_connection()
    conn.execute("DELETE FROM weather")
    conn.commit()
    release_connection(conn)

    yield

    conn = get_connection()
    conn.execute("DELETE FROM weather")
    conn.commit()
    release_connection(conn)


@pytest.fixture(autouse=True)
def disable_rate_limit(monkeypatch):
    from app import app

    def fake_limit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator

    monkeypatch.setattr(app.state.limiter, "limit", fake_limit)
