import json
import os
from pathlib import Path
from typing import Any


DEFAULT_AUDIT_PATH = "runtime/audit.jsonl"


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_audit_path() -> Path:
    configured_path = os.getenv(
        "TOOLFENCE_AUDIT_PATH",
        DEFAULT_AUDIT_PATH,
    )

    path = Path(configured_path)

    if not path.is_absolute():
        path = get_project_root() / path

    return path


def read_audit_events() -> list[dict[str, Any]]:
    path = get_audit_path()

    if not path.exists():
        return []

    events: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line_number, raw_line in enumerate(
            file,
            start=1,
        ):
            line = raw_line.strip()

            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Invalid JSON in audit log "
                    f"at line {line_number}: {path}"
                ) from exc

            if not isinstance(event, dict):
                raise ValueError(
                    "Audit log entries must be JSON objects "
                    f"(line {line_number}: {path})."
                )

            events.append(event)

    return events
