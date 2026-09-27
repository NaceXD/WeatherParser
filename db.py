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
            wind_speed INTEGER,
            condition INTEGER,
            description TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # Добавляем колонки, если таблица уже была создана без них
    columns = {row[1] for row in cursor.execute("PRAGMA table_info(weather)").fetchall()}
    if "wind_speed" not in columns:
        cursor.execute("ALTER TABLE weather ADD COLUMN wind_speed REAL")
    if "condition" not in columns:
        cursor.execute("ALTER TABLE weather ADD COLUMN condition TEXT")
    conn.commit()
    conn.close()


def save_weather(record: dict):
    conn = sqlite3.connect("weather.db")
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


init_db()
