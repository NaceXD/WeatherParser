import sqlite3
from contextlib import contextmanager
from queue import Queue
from typing import Generator

DB_NAME = "weather.db"
# Пул соединений для предотвращения постоянного переоткрытия файла
_pool: Queue[sqlite3.Connection] = Queue(maxsize=5)


def _create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False, timeout=20.0)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
    except sqlite3.Error:
        pass

    return conn


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    if _pool.empty():
        conn = _create_connection()
    else:
        conn = _pool.get_nowait()

    try:
        yield conn
    finally:
        if _pool.full():
            conn.close()
        else:
            _pool.put_nowait(conn)


def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """CREATE TABLE IF NOT EXISTS weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                temp REAL,
                humidity INTEGER,
                pressure INTEGER,
                wind_speed REAL,
                condition TEXT,
                description TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

def save_weather(record: dict):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO weather (city, temp, humidity, pressure, wind_speed, condition, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)            
            """,
            (
                record["city"],
                record["temp"],
                record["humidity"],
                record["pressure"],
                record.get("wind_speed"),
                record.get("condition"),
                record["description"],
            ),
        )
        conn.commit()

def get_history(limit: int) -> list[dict]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        result = cursor.execute(
            """"SELECT * FROM weather ORDER BY fetched_at DESC LIMIT ?""",
            (limit,)
        ).fetchall()

        return [dict(row) for row in result]