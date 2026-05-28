from __future__ import annotations

import hashlib
import hmac
import time
from urllib.parse import quote

from app.core.config import get_settings


class StorageService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def build_object_key(self, *, institution_id, module: str, entity_id, file_id, filename: str) -> str:
        safe_module = "".join(char for char in module.lower() if char.isalnum() or char in ("-", "_"))[:80]
        suffix = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
        entity_segment = str(entity_id) if entity_id else "unassigned"
        return f"institutions/{institution_id}/{safe_module}/{entity_segment}/{file_id}.{suffix}"

    def signed_url(self, *, method: str, object_key: str, expires_in_seconds: int | None = None) -> str:
        expires_in = expires_in_seconds or self.settings.signed_url_expiry_seconds
        expires_at = int(time.time()) + expires_in
        payload = f"{method.upper()}\n{object_key}\n{expires_at}".encode()
        signature = hmac.new(
            self.settings.signed_url_secret.encode(),
            payload,
            hashlib.sha256,
        ).hexdigest()
        base = self.settings.object_storage_public_base_url.rstrip("/")
        return f"{base}/{quote(object_key)}?method={method.upper()}&expires={expires_at}&signature={signature}"
