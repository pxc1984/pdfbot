from __future__ import annotations

from pathlib import Path

import redis

from bot.settings import get_settings


def get_redis() -> redis.Redis:
    settings = get_settings()
    return redis.Redis.from_url(settings.resolved_redis_url, decode_responses=True)


def try_register_user(chat_id: int, username: str = "") -> bool:
    r = get_redis()
    added = r.sadd("users", str(chat_id))
    if username:
        r.hset(f"user:{chat_id}", mapping={"username": username})
    return bool(added)


def add_photo(chat_id: int, message_id: int, image_path: str) -> int:
    r = get_redis()
    key = f"photos:{chat_id}"
    pipe = r.pipeline()
    pipe.zadd(key, {image_path: message_id})
    pipe.zcard(key)
    return int(pipe.execute()[1])


def list_photo_paths(chat_id: int) -> list[str]:
    r = get_redis()
    key = f"photos:{chat_id}"
    return list(r.zrange(key, 0, -1))


def delete_photos(chat_id: int, cleanup_files: bool = True) -> int:
    r = get_redis()
    key = f"photos:{chat_id}"
    paths = r.zrange(key, 0, -1) if cleanup_files else []
    for image_path in paths:
        try:
            Path(image_path).unlink()
        except FileNotFoundError:
            continue
    r.delete(key)
    return len(paths)


def count_photos(chat_id: int) -> int:
    r = get_redis()
    key = f"photos:{chat_id}"
    return int(r.zcard(key))
