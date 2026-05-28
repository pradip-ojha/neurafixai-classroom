from dataclasses import dataclass
from uuid import UUID

from app.models import User


@dataclass(frozen=True)
class TenantContext:
    institution_id: UUID
    user_id: UUID
    session_id: UUID
    user: User

