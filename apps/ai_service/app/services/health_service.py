from time import perf_counter

from redis.asyncio import Redis

from app.core.config import get_settings
from app.schemas.health import DependencyStatus


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

