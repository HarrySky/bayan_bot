from __future__ import annotations

from io import BytesIO
from sqlite3 import PARSE_DECLTYPES, Binary

from aiosqlite import register_adapter, register_converter
from databases import Database
from numpy import load, ndarray, save

from bayan_bot import conf


def adapt_numpy_ndarray(ndarray: ndarray) -> Binary:
    out = BytesIO()
    save(out, ndarray)
    return Binary(out.getvalue())


def convert_array_to_ndarray(text: bytes) -> ndarray:
    return load(BytesIO(text))


async def init_database() -> Database:
    database = Database(conf.DATABASE_URL, detect_types=PARSE_DECLTYPES)
    register_adapter(ndarray, adapt_numpy_ndarray)
    register_converter("array", convert_array_to_ndarray)
    await database.connect()
    return database
