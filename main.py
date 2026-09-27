import argparse

from api import get_weather
from db import save_weather, get_history


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--city", type=str, default="Krasnodar")
    parser.add_argument("--history", type=int, default=None)
    args = parser.parse_args()

    if args.history is not None:
        result = get_history(args.history)
        for i in result:
            print(
                f"{i['fetched_at']} | {i['city']} | {i['temp']}°C | "
                f"{i['description']} | Ветер: {i['wind_speed']} м/с | {i['condition']}"
            )
    else:
        weather = get_weather(args.city)
        if "error" in weather:
            print(weather["error"])
            return
        save_weather(weather)
        print(
            f"{weather['city']}: {weather['temp']}°C, {weather['description']}, "
            f"Ветер: {weather['wind_speed']} м/с | {weather['condition']}"
        )


if __name__ == "__main__":
    main()
