from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.api.services.audit_reader import read_audit_events
from app.api.services.benchmark_reader import read_benchmark_report


DEFAULT_TASK_CONFIG_PATH = "config/golden_task.json"
DEFAULT_CAPABILITY_CONFIG_PATH = "config/capabilities.json"


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_project_path(
    env_name: str,
    default_path: str,
) -> Path:
    configured = os.getenv(
        env_name,
        default_path,
    )

    path = Path(configured)

    if not path.is_absolute():
        path = get_project_root() / path

    return path


def _read_json_object(
    path: Path,
) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required ToolFence data file not found: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON in ToolFence data file: {path}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON object in ToolFence data file: {path}"
        )

    return data


def read_task_context() -> dict[str, str]:
    path = _resolve_project_path(
        "TOOLFENCE_TASK_CONFIG_PATH",
        DEFAULT_TASK_CONFIG_PATH,
    )

    data = _read_json_object(
        path
    )

    task_id = (
        data.get("task_id")
        or data.get("taskId")
        or data.get("id")
    )

    task = (
        data.get("task")
        or data.get("task_text")
        or data.get("taskText")
    )

    if (
        not isinstance(task_id, str)
        or not task_id
    ):
        raise ValueError(
            "Trusted task configuration is missing task_id."
        )

    if (
        not isinstance(task, str)
        or not task
    ):
        raise ValueError(
            "Trusted task configuration is missing task text."
        )

    return {
        "task_id": task_id,
        "task": task,
    }


def read_capability_inventory() -> list[str]:
    path = _resolve_project_path(
        "TOOLFENCE_CAPABILITY_CONFIG_PATH",
        DEFAULT_CAPABILITY_CONFIG_PATH,
    )

    data = _read_json_object(
        path
    )

    raw_capabilities = data.get(
        "capabilities",
        data,
    )

    tools: list[str] = []

    if isinstance(
        raw_capabilities,
        dict,
    ):
        for key, value in raw_capabilities.items():
            if isinstance(value, dict):
                tool = (
                    value.get("tool")
                    or value.get("name")
                    or key
                )
            else:
                tool = key

            if isinstance(tool, str):
                tools.append(tool)

    elif isinstance(
        raw_capabilities,
        list,
    ):
        for item in raw_capabilities:
            if isinstance(item, str):
                tools.append(item)
                continue

            if isinstance(item, dict):
                tool = (
                    item.get("tool")
                    or item.get("name")
                    or item.get("capability")
                )

                if isinstance(tool, str):
                    tools.append(tool)

    else:
        raise ValueError(
            "Unsupported capability inventory structure."
        )

    tools = list(
        dict.fromkeys(tools)
    )

    if not tools:
        raise ValueError(
            "Capability inventory contains no tools."
        )

    return tools


def normalize_audit_events() -> list[
    dict[str, Any]
]:
    raw_events = read_audit_events()

    normalized: list[
        dict[str, Any]
    ] = []

    for index, event in enumerate(
        raw_events,
        start=1,
    ):
        event_id = (
            event.get("event_id")
            or event.get("eventId")
            or event.get("id")
            or index
        )

        task_id = (
            event.get("task_id")
            or event.get("taskId")
        )

        policy_id = (
            event.get("policy_id")
            or event.get("policyId")
        )

        tool = (
            event.get("tool")
            or event.get("capability")
            or ""
        )

        resource = (
            event.get("resource")
            or ""
        )

        decision = (
            event.get("decision")
            or ""
        )

        reason_code = (
            event.get("reason_code")
            or event.get("reasonCode")
            or ""
        )

        execution_status = (
            event.get("execution_status")
            or event.get("executionStatus")
            or ""
        )

        timestamp = (
            event.get("timestamp")
            or event.get("created_at")
            or event.get("createdAt")
        )

        normalized.append(
            {
                "event_id": int(
                    event_id
                ),
                "task_id": (
                    str(task_id)
                    if task_id is not None
                    else None
                ),
                "policy_id": (
                    str(policy_id)
                    if policy_id is not None
                    else None
                ),
                "tool": str(tool),
                "resource": str(
                    resource
                ),
                "decision": str(
                    decision
                ),
                "reason_code": str(
                    reason_code
                ),
                "execution_status": str(
                    execution_status
                ),
                "timestamp": (
                    str(timestamp)
                    if timestamp is not None
                    else None
                ),
            }
        )

    return normalized


def _required_number(
    data: dict[str, Any],
    key: str,
) -> float:
    value = data.get(
        key
    )

    if isinstance(
        value,
        bool,
    ):
        raise ValueError(
            f"Benchmark metric {key!r} must be numeric."
        )

    if isinstance(
        value,
        (int, float),
    ):
        return float(value)

    raise ValueError(
        f"Benchmark report is missing metric: {key}"
    )


def _percentage(
    ratio: float,
) -> float:
    """
    Convert benchmark ratios in the range 0..1 to percentages.
    """

    return round(
        ratio * 100,
        2,
    )


def normalize_benchmark_report() -> dict[
    str,
    Any,
]:
    """
    Normalize runtime/benchmark_report.json for the dashboard API.

    The benchmark runner stores accuracy/reduction values as ratios,
    while the frontend API exposes human-readable percentages.
    """

    report = read_benchmark_report()

    metrics = report.get(
        "metrics"
    )

    if not isinstance(
        metrics,
        dict,
    ):
        raise ValueError(
            "Benchmark report is missing the 'metrics' object."
        )

    total_cases = int(
        _required_number(
            metrics,
            "total_cases",
        )
    )

    matched_cases = int(
        _required_number(
            metrics,
            "correct_cases",
        )
    )

    ground_truth_match_rate = (
        _required_number(
            metrics,
            "ground_truth_match_rate",
        )
    )

    forbidden_blocking_rate = (
        _required_number(
            metrics,
            "forbidden_action_blocking_rate",
        )
    )

    false_denial_rate = (
        _required_number(
            metrics,
            "false_denial_rate",
        )
    )

    boundary_accuracy = (
        _required_number(
            metrics,
            "boundary_case_accuracy",
        )
    )

    privilege_reduction_ratio = (
        _required_number(
            metrics,
            "privilege_reduction_ratio",
        )
    )

    mean_evaluation_ms = (
        _required_number(
            metrics,
            "mean_authorization_evaluation_ms",
        )
    )

    max_evaluation_ms = (
        _required_number(
            metrics,
            "max_authorization_evaluation_ms",
        )
    )

    return {
        "total_cases": total_cases,
        "matched_cases": matched_cases,
        "ground_truth_match_percent": (
            _percentage(
                ground_truth_match_rate
            )
        ),
        "forbidden_action_blocking_percent": (
            _percentage(
                forbidden_blocking_rate
            )
        ),
        "false_denial_percent": (
            _percentage(
                false_denial_rate
            )
        ),
        "boundary_accuracy_percent": (
            _percentage(
                boundary_accuracy
            )
        ),
        "privilege_reduction_percent": (
            _percentage(
                privilege_reduction_ratio
            )
        ),
        "mean_policy_evaluation_ms": (
            mean_evaluation_ms
        ),
        "max_policy_evaluation_ms": (
            max_evaluation_ms
        ),
    }


def get_latest_policy_id() -> str | None:
    events = normalize_audit_events()

    for event in reversed(
        events
    ):
        policy_id = event.get(
            "policy_id"
        )

        if (
            isinstance(
                policy_id,
                str,
            )
            and policy_id
        ):
            return policy_id

    return None
