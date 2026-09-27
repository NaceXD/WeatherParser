import sqlite3


def init_db():
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT,
            temp REAL,
            humidity INTEGER,
            pressure INTEGER,
            description TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def save_weather(record: dict):
    conn = sqlite3.connect("weather.db")
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO weather (city, temp, humidity, pressure, description) VALUES (?, ?, ?, ?, ?)
        """,
        (record["city"], record["temp"], record["humidity"], record["pressure"], record["description"]),
    )
    conn.commit()
    conn.close()


def get_history(limit: int) -> list[dict]:
    conn = sqlite3.connect("weather.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    result = cursor.execute(
        """SELECT * FROM weather ORDER BY fetched_at DESC LIMIT ?
        """,
        (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in result]
