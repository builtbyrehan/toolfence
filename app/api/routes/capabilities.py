from __future__ import annotations

from collections import defaultdict
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.schemas.capability import (
    CapabilitiesResponse,
    CapabilityResponse,
)
from app.application import load_capability_inventory
from app.policy.runtime_snapshot import read_policy_snapshot


router = APIRouter()


def _active_grants(
    snapshot: dict[str, Any] | None,
) -> dict[str, list[str]]:
    """
    Return effective grants from an ACTIVE runtime policy snapshot.

    Historical COMPLETED / REVOKED / EXPIRED snapshots do not represent
    currently usable permissions, so they return no effective grants.
    """

    if snapshot is None:
        return {}

    if snapshot.get("state") != "ACTIVE":
        return {}

    raw_grants = snapshot.get("allowed")

    if not isinstance(raw_grants, list):
        raise ValueError(
            "Runtime policy snapshot field 'allowed' "
            "must be a list."
        )

    grants: dict[str, list[str]] = defaultdict(
        list
    )

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

        grants[tool].append(
            resource
        )

    return dict(grants)


@router.get(
    "/capabilities",
    response_model=CapabilitiesResponse,
)
def get_capabilities() -> CapabilitiesResponse:
    try:
        inventory = load_capability_inventory()

        snapshot = read_policy_snapshot()

        grants_by_tool = _active_grants(
            snapshot
        )

        capabilities: list[
            CapabilityResponse
        ] = []

        granted_count = 0

        for capability in inventory.capabilities:
            scopes = grants_by_tool.get(
                capability.tool,
                [],
            )

            granted = bool(scopes)

            if granted:
                granted_count += 1

            # Current frontend schema displays one resource string.
            # Multiple scopes, if ever present for a tool, remain visible
            # rather than being silently discarded.
            resource = (
                " | ".join(
                    sorted(
                        set(scopes)
                    )
                )
                if scopes
                else None
            )

            capabilities.append(
                CapabilityResponse(
                    tool=capability.tool,
                    granted=granted,
                    resource=resource,
                )
            )

        total = len(capabilities)

        excluded = (
            total
            - granted_count
        )

        privilege_reduction_percent = (
            round(
                (excluded / total) * 100,
                2,
            )
            if total
            else 0.0
        )

        return CapabilitiesResponse(
            total=total,
            granted=granted_count,
            excluded=excluded,
            privilege_reduction_percent=(
                privilege_reduction_percent
            ),
            capabilities=capabilities,
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
