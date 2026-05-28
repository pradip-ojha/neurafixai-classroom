import json
from uuid import UUID

from redis.asyncio import Redis

from app.core.config import get_settings


class PermissionCache:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def get_user_permissions(self, institution_id: UUID, user_id: UUID) -> set[str] | None:
        client = Redis.from_url(self.settings.redis_url, encoding="utf-8", decode_responses=True)
        try:
            raw = await client.get(self._key(institution_id, user_id))
            if raw is None:
                return None
            return set(json.loads(raw))
        except Exception:
            return None
        finally:
            await client.aclose()

    async def set_user_permissions(
        self,
        institution_id: UUID,
        user_id: UUID,
        permissions: set[str],
        ttl_seconds: int = 300,
    ) -> None:
        client = Redis.from_url(self.settings.redis_url, encoding="utf-8", decode_responses=True)
        try:
            await client.setex(
                self._key(institution_id, user_id),
                ttl_seconds,
                json.dumps(sorted(permissions)),
            )
        except Exception:
            return
        finally:
            await client.aclose()

    async def invalidate_user_permissions(self, institution_id: UUID, user_id: UUID) -> None:
        client = Redis.from_url(self.settings.redis_url, encoding="utf-8", decode_responses=True)
        try:
            await client.delete(self._key(institution_id, user_id))
        except Exception:
            return
        finally:
            await client.aclose()

    @staticmethod
    def _key(institution_id: UUID, user_id: UUID) -> str:
        return f"permissions:{institution_id}:{user_id}"

