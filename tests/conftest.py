import pytest
from db import init_db, get_connection, release_connection


@pytest.fixture(autouse=True)
def setup_db():
    init_db()

    # Очищаем таблицу перед тестом
    conn = get_connection()
    conn.execute("DELETE FROM weather")
    conn.commit()
    release_connection(conn)

    yield

    # Очищаем после теста
    conn = get_connection()
    conn.execute("DELETE FROM weather")
    conn.commit()
    release_connection(conn)