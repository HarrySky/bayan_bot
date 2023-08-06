from __future__ import annotations

from os import getenv

BOT_TOKEN: str = ""
GROUP_CHAT_ID: int = 0
DATABASE_URL: str = ""


def init_config() -> None:
    global BOT_TOKEN, GROUP_CHAT_ID, DATABASE_URL

    BOT_TOKEN = getenv("BOT_TOKEN", "")
    GROUP_CHAT_ID = int(getenv("GROUP_CHAT_ID", 0))
    DATABASE_URL = getenv("DATABASE_URL", "")

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not defined")

    if GROUP_CHAT_ID >= 0:
        raise ValueError(f"GROUP_CHAT_ID not defined or wrong: {GROUP_CHAT_ID}")

    if not DATABASE_URL:
        raise ValueError("DATABASE_URL not defined")

    if not DATABASE_URL.startswith("sqlite:/"):
        raise ValueError(f"Only sqlite is supported, fix DATABASE_URL: {DATABASE_URL}")
