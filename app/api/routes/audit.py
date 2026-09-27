from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.schemas.audit import (
    AuditEventResponse,
    AuditResponse,
)
from app.api.services.dashboard import normalize_audit_events


router = APIRouter()


@router.get(
    "/audit",
    response_model=AuditResponse,
)
def get_audit_log() -> AuditResponse:
    """
    Return ToolFence authorization audit evidence.

    The API is read-only. Audit events continue to be written exclusively
    by the trusted dispatcher/audit subsystem.
    """

    try:
        raw_events = normalize_audit_events()

        events = [
            AuditEventResponse(
                event_id=event["event_id"],
                task_id=event["task_id"],
                policy_id=event["policy_id"],
                tool=event["tool"],
                resource=event["resource"],
                decision=event["decision"],
                reason_code=event["reason_code"],
                execution_status=event[
                    "execution_status"
                ],
                timestamp=event["timestamp"],
            )
            for event in raw_events
        ]

        return AuditResponse(
            total=len(events),
            events=events,
        )

    except (
        OSError,
        TypeError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
