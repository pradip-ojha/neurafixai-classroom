from time import perf_counter

from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import get_settings
from app.db.session import engine
from app.schemas.health import DependencyStatus


async def check_database() -> DependencyStatus:
    start = perf_counter()
    try:
        async with engine.connect() as connection:
            await connection.execute(text("select 1"))
        return DependencyStatus(name="postgres", ok=True, latency_ms=_elapsed_ms(start))
    except Exception as exc:
        return DependencyStatus(
            name="postgres",
            ok=False,
            latency_ms=_elapsed_ms(start),
            error=exc.__class__.__name__,
        )


async def check_redis() -> DependencyStatus:
    start = perf_counter()
    settings = get_settings()
    client = Redis.from_url(settings.redis_url, encoding="utf-8", decode_responses=True)
    try:
        await client.ping()
        return DependencyStatus(name="redis", ok=True, latency_ms=_elapsed_ms(start))
    except Exception as exc:
        return DependencyStatus(
            name="redis",
            ok=False,
            latency_ms=_elapsed_ms(start),
            error=exc.__class__.__name__,
        )
    finally:
        await client.aclose()


def _elapsed_ms(start: float) -> float:
    return round((perf_counter() - start) * 1000, 2)

