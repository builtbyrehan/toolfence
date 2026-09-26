from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Callable, Literal

from pydantic import TypeAdapter, ValidationError

from app.policy.schema import TaskID, ToolName


Decision = Literal["ALLOW", "DENY"]

ExecutionStatus = Literal[
    "NOT_EXECUTED",
    "SUCCEEDED",
    "FAILED",
]


_TASK_ID_ADAPTER = TypeAdapter(TaskID)
_TOOL_NAME_ADAPTER = TypeAdapter(ToolName)


class AuditLogError(ValueError):
    """
    Raised when an audit event or persisted audit log is invalid.

    Attributes:
        code:
            Stable machine-readable error code.

        message:
            Human-readable explanation.
    """

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: int
    timestamp: datetime

    task_id: str
    tool: str
    resource: str

    decision: Decision
    reason_code: str
    reason: str

    policy_id: str | None
    matched_scope: str | None

    execution_status: ExecutionStatus
    execution_error_code: str | None
    execution_error: str | None


def _utc_now() -> datetime:
    return datetime.now(UTC)


class AuditLog:
    """
    Append-only JSONL audit log for ToolFence protected tool calls.

    The audit log records authorization and execution metadata, but it does
    not record backend result payloads. This avoids copying sensitive tool
    outputs into the audit trail.

    Existing JSONL records are loaded when the AuditLog is created so event
    numbering continues across process restarts.
    """

    def __init__(
        self,
        path: str | Path = "runtime/audit.jsonl",
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._path = Path(path)
        self._clock = clock or _utc_now
        self._lock = RLock()

        self._events: list[AuditEvent] = []

        self._load_existing()

    @property
    def path(self) -> Path:
        return self._path

    def record(
        self,
        *,
        task_id: str,
        tool: str,
        resource: str,
        decision: Decision,
        reason_code: str,
        reason: str,
        policy_id: str | None,
        matched_scope: str | None,
        execution_status: ExecutionStatus,
        execution_error_code: str | None = None,
        execution_error: str | None = None,
    ) -> AuditEvent:
        """
        Persist one authorization/execution audit event.

        Backend result payloads are intentionally not accepted.
        """
        validated_task_id = self._validate_task_id(task_id)
        validated_tool = self._validate_tool(tool)

        self._validate_resource(resource)
        self._validate_decision(decision)
        self._validate_reason_code(reason_code)
        self._validate_text(
            reason,
            field_name="reason",
            maximum=1000,
        )

        self._validate_policy_id(policy_id)

        if matched_scope is not None:
            self._validate_resource(matched_scope)

        self._validate_execution_status(execution_status)

        self._validate_optional_text(
            execution_error_code,
            field_name="execution_error_code",
            maximum=128,
        )

        self._validate_optional_text(
            execution_error,
            field_name="execution_error",
            maximum=1000,
        )

        if execution_status == "NOT_EXECUTED":
            if (
                execution_error_code is not None
                or execution_error is not None
            ):
                raise AuditLogError(
                    "INVALID_EXECUTION_METADATA",
                    (
                        "NOT_EXECUTED events cannot contain "
                        "execution errors."
                    ),
                )

        if execution_status == "SUCCEEDED":
            if (
                execution_error_code is not None
                or execution_error is not None
            ):
                raise AuditLogError(
                    "INVALID_EXECUTION_METADATA",
                    (
                        "SUCCEEDED events cannot contain "
                        "execution errors."
                    ),
                )

        if execution_status == "FAILED":
            if execution_error_code is None:
                raise AuditLogError(
                    "INVALID_EXECUTION_METADATA",
                    (
                        "FAILED events require an "
                        "execution_error_code."
                    ),
                )

        timestamp = self._now()

        with self._lock:
            event = AuditEvent(
                event_id=len(self._events) + 1,
                timestamp=timestamp,
                task_id=validated_task_id,
                tool=validated_tool,
                resource=resource,
                decision=decision,
                reason_code=reason_code,
                reason=reason,
                policy_id=policy_id,
                matched_scope=matched_scope,
                execution_status=execution_status,
                execution_error_code=execution_error_code,
                execution_error=execution_error,
            )

            self._append_event(event)

            self._events.append(event)

            return event

    def events(
        self,
        *,
        task_id: str | None = None,
    ) -> tuple[AuditEvent, ...]:
        """
        Return immutable audit event snapshots.

        When task_id is supplied, only that task's events are returned.
        """
        with self._lock:
            if task_id is None:
                return tuple(self._events)

            validated_task_id = self._validate_task_id(task_id)

            return tuple(
                event
                for event in self._events
                if event.task_id == validated_task_id
            )

    def _load_existing(self) -> None:
        if not self._path.exists():
            return

        if not self._path.is_file():
            raise AuditLogError(
                "INVALID_AUDIT_PATH",
                (
                    f"Audit path is not a regular file: "
                    f"{self._path}"
                ),
            )

        loaded: list[AuditEvent] = []

        try:
            with self._path.open(
                "r",
                encoding="utf-8",
            ) as handle:
                for line_number, raw_line in enumerate(
                    handle,
                    start=1,
                ):
                    if not raw_line.strip():
                        continue

                    try:
                        data = json.loads(raw_line)
                    except json.JSONDecodeError as exc:
                        raise AuditLogError(
                            "CORRUPT_AUDIT_LOG",
                            (
                                "Invalid JSON in audit log at "
                                f"line {line_number}."
                            ),
                        ) from exc

                    event = self._event_from_dict(
                        data,
                        line_number=line_number,
                    )

                    expected_id = len(loaded) + 1

                    if event.event_id != expected_id:
                        raise AuditLogError(
                            "CORRUPT_AUDIT_LOG",
                            (
                                "Audit event IDs are not sequential "
                                f"at line {line_number}."
                            ),
                        )

                    loaded.append(event)

        except OSError as exc:
            raise AuditLogError(
                "AUDIT_READ_FAILED",
                "Unable to read the audit log.",
            ) from exc

        self._events = loaded

    def _append_event(
        self,
        event: AuditEvent,
    ) -> None:
        payload = asdict(event)

        payload["timestamp"] = (
            event.timestamp
            .astimezone(UTC)
            .isoformat()
        )

        try:
            self._path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            with self._path.open(
                "a",
                encoding="utf-8",
                newline="\n",
            ) as handle:
                handle.write(
                    json.dumps(
                        payload,
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                )

                handle.write("\n")
                handle.flush()

        except OSError as exc:
            raise AuditLogError(
                "AUDIT_WRITE_FAILED",
                "Unable to persist the audit event.",
            ) from exc

    def _event_from_dict(
        self,
        data: object,
        *,
        line_number: int,
    ) -> AuditEvent:
        if not isinstance(data, dict):
            raise AuditLogError(
                "CORRUPT_AUDIT_LOG",
                (
                    "Audit event must be a JSON object at "
                    f"line {line_number}."
                ),
            )

        expected_fields = {
            "event_id",
            "timestamp",
            "task_id",
            "tool",
            "resource",
            "decision",
            "reason_code",
            "reason",
            "policy_id",
            "matched_scope",
            "execution_status",
            "execution_error_code",
            "execution_error",
        }

        if set(data) != expected_fields:
            raise AuditLogError(
                "CORRUPT_AUDIT_LOG",
                (
                    "Audit event contains missing or unknown "
                    f"fields at line {line_number}."
                ),
            )

        event_id = data["event_id"]

        if type(event_id) is not int or event_id < 1:
            raise AuditLogError(
                "CORRUPT_AUDIT_LOG",
                (
                    "Invalid audit event_id at "
                    f"line {line_number}."
                ),
            )

        timestamp_raw = data["timestamp"]

        if not isinstance(timestamp_raw, str):
            raise AuditLogError(
                "CORRUPT_AUDIT_LOG",
                (
                    "Invalid audit timestamp at "
                    f"line {line_number}."
                ),
            )

        try:
            timestamp = datetime.fromisoformat(
                timestamp_raw
            )
        except ValueError as exc:
            raise AuditLogError(
                "CORRUPT_AUDIT_LOG",
                (
                    "Invalid audit timestamp at "
                    f"line {line_number}."
                ),
            ) from exc

        if (
            timestamp.tzinfo is None
            or timestamp.utcoffset() is None
        ):
            raise AuditLogError(
                "CORRUPT_AUDIT_LOG",
                (
                    "Audit timestamp must be timezone-aware "
                    f"at line {line_number}."
                ),
            )

        try:
            task_id = self._validate_task_id(
                data["task_id"]
            )

            tool = self._validate_tool(
                data["tool"]
            )

            resource = data["resource"]

            self._validate_resource(resource)

            decision = data["decision"]

            self._validate_decision(decision)

            reason_code = data["reason_code"]

            self._validate_reason_code(reason_code)

            reason = data["reason"]

            self._validate_text(
                reason,
                field_name="reason",
                maximum=1000,
            )

            policy_id = data["policy_id"]

            self._validate_policy_id(policy_id)

            matched_scope = data["matched_scope"]

            if matched_scope is not None:
                self._validate_resource(matched_scope)

            execution_status = data["execution_status"]

            self._validate_execution_status(
                execution_status
            )

            execution_error_code = data[
                "execution_error_code"
            ]

            self._validate_optional_text(
                execution_error_code,
                field_name="execution_error_code",
                maximum=128,
            )

            execution_error = data[
                "execution_error"
            ]

            self._validate_optional_text(
                execution_error,
                field_name="execution_error",
                maximum=1000,
            )

        except (AuditLogError, ValueError) as exc:
            raise AuditLogError(
                "CORRUPT_AUDIT_LOG",
                (
                    "Invalid audit event data at "
                    f"line {line_number}."
                ),
            ) from exc

        return AuditEvent(
            event_id=event_id,
            timestamp=timestamp.astimezone(UTC),
            task_id=task_id,
            tool=tool,
            resource=resource,
            decision=decision,
            reason_code=reason_code,
            reason=reason,
            policy_id=policy_id,
            matched_scope=matched_scope,
            execution_status=execution_status,
            execution_error_code=execution_error_code,
            execution_error=execution_error,
        )

    def _now(self) -> datetime:
        now = self._clock()

        if not isinstance(now, datetime):
            raise AuditLogError(
                "INVALID_CLOCK",
                "Audit clock must return a datetime.",
            )

        if (
            now.tzinfo is None
            or now.utcoffset() is None
        ):
            raise AuditLogError(
                "INVALID_CLOCK",
                (
                    "Audit clock must return a "
                    "timezone-aware datetime."
                ),
            )

        return now.astimezone(UTC)

    @staticmethod
    def _validate_task_id(
        task_id: object,
    ) -> str:
        try:
            return _TASK_ID_ADAPTER.validate_python(
                task_id,
                strict=True,
            )
        except ValidationError as exc:
            raise ValueError(
                "Invalid audit task_id."
            ) from exc

    @staticmethod
    def _validate_tool(
        tool: object,
    ) -> str:
        try:
            return _TOOL_NAME_ADAPTER.validate_python(
                tool,
                strict=True,
            )
        except ValidationError as exc:
            raise ValueError(
                "Invalid audit tool."
            ) from exc

    @staticmethod
    def _validate_resource(
        resource: object,
    ) -> None:
        if not isinstance(resource, str):
            raise ValueError(
                "Audit resource must be a string."
            )

        if not resource:
            raise ValueError(
                "Audit resource cannot be empty."
            )

        if len(resource) > 512:
            raise ValueError(
                "Audit resource exceeds 512 characters."
            )

        if resource != resource.strip():
            raise ValueError(
                (
                    "Audit resource cannot contain "
                    "surrounding whitespace."
                )
            )

        if any(
            not character.isprintable()
            for character in resource
        ):
            raise ValueError(
                (
                    "Audit resource cannot contain "
                    "nonprintable characters."
                )
            )

    @staticmethod
    def _validate_decision(
        decision: object,
    ) -> None:
        if decision not in {"ALLOW", "DENY"}:
            raise AuditLogError(
                "INVALID_DECISION",
                "Audit decision must be ALLOW or DENY.",
            )

    @staticmethod
    def _validate_execution_status(
        execution_status: object,
    ) -> None:
        if execution_status not in {
            "NOT_EXECUTED",
            "SUCCEEDED",
            "FAILED",
        }:
            raise AuditLogError(
                "INVALID_EXECUTION_STATUS",
                (
                    "Invalid audit execution status."
                ),
            )

    @staticmethod
    def _validate_reason_code(
        reason_code: object,
    ) -> None:
        if not isinstance(reason_code, str):
            raise AuditLogError(
                "INVALID_REASON_CODE",
                "Audit reason_code must be a string.",
            )

        if not reason_code:
            raise AuditLogError(
                "INVALID_REASON_CODE",
                "Audit reason_code cannot be empty.",
            )

        if len(reason_code) > 128:
            raise AuditLogError(
                "INVALID_REASON_CODE",
                (
                    "Audit reason_code exceeds "
                    "128 characters."
                ),
            )

        if any(
            not (
                character.isupper()
                or character.isdigit()
                or character == "_"
            )
            for character in reason_code
        ):
            raise AuditLogError(
                "INVALID_REASON_CODE",
                (
                    "Audit reason_code must contain only "
                    "uppercase letters, digits, or underscores."
                ),
            )

    @staticmethod
    def _validate_policy_id(
        policy_id: object,
    ) -> None:
        if policy_id is None:
            return

        if not isinstance(policy_id, str):
            raise AuditLogError(
                "INVALID_POLICY_ID",
                "Audit policy_id must be a string or None.",
            )

        if (
            len(policy_id) != 64
            or any(
                character not in "0123456789abcdef"
                for character in policy_id
            )
        ):
            raise AuditLogError(
                "INVALID_POLICY_ID",
                "Audit policy_id must be a SHA-256 hex value.",
            )

    @staticmethod
    def _validate_text(
        value: object,
        *,
        field_name: str,
        maximum: int,
    ) -> None:
        if not isinstance(value, str):
            raise AuditLogError(
                "INVALID_AUDIT_TEXT",
                f"{field_name} must be a string.",
            )

        if not value.strip():
            raise AuditLogError(
                "INVALID_AUDIT_TEXT",
                f"{field_name} cannot be blank.",
            )

        if len(value) > maximum:
            raise AuditLogError(
                "INVALID_AUDIT_TEXT",
                (
                    f"{field_name} exceeds "
                    f"{maximum} characters."
                ),
            )

        if any(
            not character.isprintable()
            for character in value
        ):
            raise AuditLogError(
                "INVALID_AUDIT_TEXT",
                (
                    f"{field_name} cannot contain "
                    "nonprintable characters."
                ),
            )

    @classmethod
    def _validate_optional_text(
        cls,
        value: object,
        *,
        field_name: str,
        maximum: int,
    ) -> None:
        if value is None:
            return

        cls._validate_text(
            value,
            field_name=field_name,
            maximum=maximum,
        )