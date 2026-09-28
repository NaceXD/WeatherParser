import asyncio
import argparse

from api import get_weather
from db import save_weather, get_history, init_db


def main():
    init_db()

    parser = argparse.ArgumentParser(description="Консольная утилита для парсинга и просмотра погоды.")
    parser.add_argument("--city", type=str, default="Krasnodar", help="Название города для парсинга погоды")
    parser.add_argument("--history", type=int, default=None,
                        help="Вывести указанное количество последних запросов из базы")
    args = parser.parse_args()

    if args.history is not None:
        # Защита от ввода некорректного лимита
        if args.history <= 0:
            print("Ошибка: Лимит истории должен быть больше 0.")
            return

        result = get_history(args.history)
        if not result:
            print("История запросов пуста.")
            return

        print(f"--- Последние {len(result)} запросов погоды ---")
        for i in result:
            print(
                f"{i['fetched_at']} | {i['city']} | {i['temp']}°C | "
                f"{i['description']} | Ветер: {i['wind_speed']} м/с | {i['condition']}"
            )
    else:
        weather = asyncio.run(get_weather(args.city))
        if "error" in weather:
            print(f"Ошибка: {weather["error"]}")
            return

        save_weather(weather)

        print("Погода успешно сохранена в БД!")
        print(
            f"{weather['city']}: {weather['temp']}°C, {weather['description']}, "
            f"Ветер: {weather['wind_speed']} м/с | {weather['condition']}"
        )


if __name__ == "__main__":
    main()
