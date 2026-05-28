from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


class AuditService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def record(
        self,
        *,
        action: str,
        institution_id: UUID | None,
        actor_user_id: UUID | None,
        entity_type: str | None = None,
        entity_id: UUID | None = None,
        old_values: dict | None = None,
        new_values: dict | None = None,
        metadata: dict | None = None,
        request_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> None:
        self.session.add(
            AuditLog(
                institution_id=institution_id,
                actor_user_id=actor_user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                old_values=old_values,
                new_values=new_values,
                metadata_json=metadata,
                request_id=request_id,
                ip_address=ip_address,
                user_agent=user_agent,
            )
        )

