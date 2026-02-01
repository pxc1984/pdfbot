from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

import psycopg

from bot.settings import get_settings


@contextmanager
def db_connection() -> Iterable[psycopg.Connection]:
    settings = get_settings()
    conn = psycopg.connect(settings.resolved_database_url)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def try_register_user(chat_id: int, username: str = "") -> bool:
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO users (chat_id, username)
                VALUES (%s, %s)
                ON CONFLICT (chat_id) DO NOTHING
                """,
                (chat_id, username),
            )
            return cur.rowcount == 1


def add_photo(chat_id: int, message_id: int, image_path: str) -> int:
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO photos (chat_id, message_id, image_path)
                VALUES (%s, %s, %s)
                """,
                (chat_id, message_id, image_path),
            )
            cur.execute("SELECT COUNT(*) FROM photos WHERE chat_id = %s", (chat_id,))
            return int(cur.fetchone()[0])


def list_photo_paths(chat_id: int) -> list[str]:
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT image_path
                FROM photos
                WHERE chat_id = %s
                ORDER BY message_id ASC
                """,
                (chat_id,),
            )
            return [row[0] for row in cur.fetchall()]


def delete_photos(chat_id: int, cleanup_files: bool = True) -> int:
    with db_connection() as conn:
        with conn.cursor() as cur:
            if cleanup_files:
                cur.execute(
                    """
                    SELECT image_path
                    FROM photos
                    WHERE chat_id = %s
                    """,
                    (chat_id,),
                )
                for (image_path,) in cur.fetchall():
                    try:
                        Path(image_path).unlink()
                    except FileNotFoundError:
                        continue
            cur.execute("DELETE FROM photos WHERE chat_id = %s", (chat_id,))
            return cur.rowcount


def count_photos(chat_id: int) -> int:
    with db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM photos WHERE chat_id = %s", (chat_id,))
            return int(cur.fetchone()[0])
