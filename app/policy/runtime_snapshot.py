from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.policy.compiler import CompiledPolicy


DEFAULT_POLICY_SNAPSHOT_PATH = "runtime/active_policy.json"


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_policy_snapshot_path() -> Path:
    configured = os.getenv(
        "TOOLFENCE_POLICY_SNAPSHOT_PATH",
        DEFAULT_POLICY_SNAPSHOT_PATH,
    )

    path = Path(configured)

    if not path.is_absolute():
        path = get_project_root() / path

    return path


def _serialize_datetime(
    value: datetime | None,
) -> str | None:
    if value is None:
        return None

    return value.isoformat()


def _serialize_grant(
    grant: object,
) -> dict[str, Any]:
    if is_dataclass(grant):
        data = asdict(grant)

        if isinstance(data, dict):
            return data

    model_dump = getattr(
        grant,
        "model_dump",
        None,
    )

    if callable(model_dump):
        data = model_dump()

        if isinstance(data, dict):
            return data

    data: dict[str, Any] = {}

    for attribute in (
        "tool",
        "resource",
        "scope",
    ):
        if hasattr(grant, attribute):
            data[attribute] = getattr(
                grant,
                attribute,
            )

    if not data:
        raise TypeError(
            "Unsupported compiled grant representation."
        )

    return data


def write_policy_snapshot(
    policy: CompiledPolicy,
    *,
    state: str,
    activated_at: datetime,
    expires_at: datetime | None,
    ended_at: datetime | None,
    end_reason: str | None,
) -> Path:
    if not isinstance(
        policy,
        CompiledPolicy,
    ):
        raise TypeError(
            "policy must be a CompiledPolicy."
        )

    path = get_policy_snapshot_path()

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    snapshot = {
        "schema_version": "1.0",
        "task_id": policy.task_id,
        "task": policy.task,
        "policy_id": policy.policy_id,
        "state": state,
        "activated_at": _serialize_datetime(
            activated_at
        ),
        "expires_at": _serialize_datetime(
            expires_at
        ),
        "ended_at": _serialize_datetime(
            ended_at
        ),
        "end_reason": end_reason,
        "allowed": [
            _serialize_grant(grant)
            for grant in policy.allowed
        ],
    }

    temporary_path = path.with_suffix(
        path.suffix + ".tmp"
    )

    with temporary_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            snapshot,
            file,
            indent=2,
            sort_keys=True,
        )

        file.write("\n")

    temporary_path.replace(path)

    return path


def read_policy_snapshot() -> dict[str, Any] | None:
    path = get_policy_snapshot_path()

    if not path.exists():
        return None

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid runtime policy snapshot: {path}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Runtime policy snapshot must contain "
            "a JSON object."
        )

    return data
