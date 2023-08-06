from __future__ import annotations

from asyncio import run, sleep
from logging import getLogger

import uvloop

from bayan_bot import conf
from bayan_bot.bot import KabakBot
from bayan_bot.db import init_database
from bayan_bot.image_hashes import ImageChecker
from bayan_bot.log import init_logger

logger = getLogger("bayan_bot")


async def _main() -> None:
    conf.init_config()
    init_logger()

    logger.info("Initializing database")
    database = await init_database()

    checker = ImageChecker(database, cutoff=5)
    logger.info("Loading hashes from database")
    await checker.load_hashes()

    bot = KabakBot(conf.BOT_TOKEN, conf.GROUP_CHAT_ID, database, checker)
    logger.info("Loading bot state from database")
    await bot.load_state()
    while True:
        await bot.loop_iteration()
        await sleep(10)


def main() -> None:
    uvloop.install()
    run(_main())
