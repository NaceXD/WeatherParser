import sqlite3
from queue import Queue

DB_NAME = "weather.db"
_pool: Queue[sqlite3.Connection] = Queue(maxsize=5)


def _create_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def get_connection() -> sqlite3.Connection:
    if _pool.empty():
        return _create_connection()
    return _pool.get_nowait()


def release_connection(conn: sqlite3.Connection):
    if _pool.full():
        conn.close()
    else:
        _pool.put_nowait(conn)


def init_db():
    conn = get_connection()
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
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(weather)").fetchall()}
    if "wind_speed" not in columns:
        cursor.execute("ALTER TABLE weather ADD COLUMN wind_speed REAL")
    if "condition" not in columns:
        cursor.execute("ALTER TABLE weather ADD COLUMN condition TEXT")
    conn.commit()
    release_connection(conn)


def save_weather(record: dict):
    conn = get_connection()
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
            record["wind_speed"],
            record["condition"],
            record["description"],
        ),
    )
    conn.commit()
    release_connection(conn)


def get_history(limit: int) -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor()
    result = cursor.execute(
        """SELECT * FROM weather ORDER BY fetched_at DESC LIMIT ?""",
        (limit,)
    ).fetchall()
    release_connection(conn)
    return [dict(row) for row in result]
