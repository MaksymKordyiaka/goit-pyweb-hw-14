import os
from fastapi import HTTPException
from redis import Redis

redis_client = Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0)

RATE_LIMIT = 5  # Максимальна кількість запитів
TIME_FRAME = 60  # У секундах


def limit_rate(user_id: str):
    """
    Лімітує кількість запитів для користувача за допомогою Redis.

    Перевіряє кількість запитів від користувача за вказаний інтервал часу.
    Якщо користувач перевищує дозволену кількість запитів, піднімається помилка HTTP 429.

    :param user_id: Унікальний ідентифікатор користувача.
    :type user_id: str
    :raises HTTPException: Якщо користувач перевищує ліміт запитів, повертається помилка 429.
    """
    key = f"rate_limit:{user_id}"
    current_count = redis_client.get(key)

    if current_count is None:
        redis_client.set(key, 1, ex=TIME_FRAME)
    elif int(current_count) < RATE_LIMIT:
        redis_client.incr(key)
    else:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
