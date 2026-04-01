from asyncpg import create_pool, Pool, Connection
from fastapi import Depends

from contextlib import asynccontextmanager
from os import getenv
from os.path import join, split
from typing import Annotated, AsyncGenerator, Optional

_pool: Optional[Pool] = None
_dir_path, _ = split(__file__)


async def run_sql_command(conn, *args: str) -> None:
    with open(join(_dir_path, "scripts", *args), "r", encoding="utf-8") as f:
        await conn.execute(f.read())


async def setup_database() -> None:
    if _pool is None:
        raise RuntimeError("Connection pool is not initialized.")

    async with _pool.acquire() as conn:
        async with conn.transaction():
            await run_sql_command(conn, "tables", "sid_image.sql")
            await run_sql_command(conn, "tables", "teams.sql")
            await run_sql_command(conn, "tables", "users.sql")
            await run_sql_command(conn, "triggers", "sid_image_update_verify.sql")
            await run_sql_command(conn, "triggers", "team_autoremove.sql")
            await run_sql_command(conn, "triggers", "team_member_limit.sql")


@asynccontextmanager
async def setup_connection_pool() -> AsyncGenerator[Pool, None]:
    global _pool
    if _pool is not None:
        raise RuntimeError("Connection pool is already initialized.")

    DSN = getenv(
        "POSTGRES_DB_URL",
        "postgresql://user:password@localhost:5432/database"
    )
    MIN_SIZE = int(getenv("POSTGRES_POOL_MIN_SIZE", "5"))
    MAX_SIZE = int(getenv("POSTGRES_POOL_MAX_SIZE", "20"))

    pool = await create_pool(
        dsn=DSN,
        min_size=MIN_SIZE,
        max_size=MAX_SIZE
    )

    try:
        _pool = pool
        await setup_database()
        yield pool
    finally:
        await pool.close()
        _pool = None


async def _get_connection() -> AsyncGenerator[Connection, None]:
    if _pool is None:
        raise RuntimeError("Connection pool is not initialized.")

    async with _pool.acquire() as connection:
        yield connection  # type: ignore

get_connection = asynccontextmanager(_get_connection)

conn_depends = Depends(_get_connection, use_cache=False)
ConnDepends = Annotated[Connection, conn_depends]
