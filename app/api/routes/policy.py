from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.schemas.policy import (
    CapabilityGrantResponse,
    PolicyResponse,
)
from app.policy.runtime_snapshot import read_policy_snapshot


router = APIRouter()


def _require_string(
    data: dict[str, Any],
    key: str,
) -> str:
    value = data.get(key)

    if not isinstance(value, str) or not value:
        raise ValueError(
            f"Runtime policy snapshot is missing {key!r}."
        )

    return value


def _normalize_grants(
    raw_grants: Any,
) -> list[CapabilityGrantResponse]:
    if not isinstance(raw_grants, list):
        raise ValueError(
            "Runtime policy snapshot field 'allowed' "
            "must be a list."
        )

    grants: list[CapabilityGrantResponse] = []

    for index, raw_grant in enumerate(
        raw_grants,
    ):
        if not isinstance(raw_grant, dict):
            raise ValueError(
                "Runtime policy snapshot contains an "
                f"invalid grant at index {index}."
            )

        tool = raw_grant.get("tool")

        resource = (
            raw_grant.get("resource")
            or raw_grant.get("scope")
        )

        if not isinstance(tool, str) or not tool:
            raise ValueError(
                "Runtime policy snapshot grant is "
                f"missing tool at index {index}."
            )

        if (
            not isinstance(resource, str)
            or not resource
        ):
            raise ValueError(
                "Runtime policy snapshot grant is "
                f"missing resource scope at index {index}."
            )

        grants.append(
            CapabilityGrantResponse(
                tool=tool,
                resource=resource,
            )
        )

    return grants


@router.get(
    "/policy",
    response_model=PolicyResponse,
)
def get_policy() -> PolicyResponse:
    try:
        snapshot = read_policy_snapshot()

        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail=(
                    "No runtime policy snapshot exists yet. "
                    "Activate a ToolFence task policy first."
                ),
            )

        task_id = _require_string(
            snapshot,
            "task_id",
        )

        policy_id = _require_string(
            snapshot,
            "policy_id",
        )

        status = _require_string(
            snapshot,
            "state",
        )

        if status not in {
            "ACTIVE",
            "COMPLETED",
            "REVOKED",
            "EXPIRED",
        }:
            raise ValueError(
                "Runtime policy snapshot contains "
                f"unsupported state: {status!r}."
            )

        grants = _normalize_grants(
            snapshot.get("allowed")
        )

        return PolicyResponse(
            task_id=task_id,
            policy_id=policy_id,
            status=status,
            grants=grants,
            granted_count=len(grants),
        )

    except HTTPException:
        raise

    except (
        OSError,
        TypeError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
