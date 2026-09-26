from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from threading import RLock
from typing import Callable, Literal

from pydantic import TypeAdapter, ValidationError

from app.policy.compiler import CompiledPolicy
from app.policy.schema import TaskID


PolicyState = Literal[
    "ACTIVE",
    "COMPLETED",
    "REVOKED",
    "EXPIRED",
]


_TASK_ID_ADAPTER = TypeAdapter(TaskID)


class PolicyStoreError(ValueError):
    """
    Raised when the active-policy lifecycle cannot perform an operation.

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
class PolicyLifecycleRecord:
    task_id: str
    policy_id: str
    state: PolicyState
    activated_at: datetime
    expires_at: datetime | None
    ended_at: datetime | None
    end_reason: str | None


@dataclass(slots=True)
class _StoredPolicy:
    policy: CompiledPolicy
    lifecycle: PolicyLifecycleRecord


def _utc_now() -> datetime:
    return datetime.now(UTC)


class ActivePolicyStore:
    """
    Trusted in-memory store for activated ToolFence task policies.

    The runtime caller should provide only a task_id. The gateway can then
    retrieve the trusted active CompiledPolicy from this store.

    A caller must never be allowed to choose an arbitrary CompiledPolicy
    for an individual protected tool request.

    This MVP implementation is in-memory. A later persistence layer can
    replace it without changing the basic lifecycle semantics.
    """

    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._clock = clock or _utc_now
        self._lock = RLock()
        self._records: dict[str, _StoredPolicy] = {}

    def activate(
        self,
        policy: CompiledPolicy,
        *,
        expires_at: datetime | None = None,
    ) -> PolicyLifecycleRecord:
        """
        Activate one compiled policy for its task.

        Activation is intended to be called only by trusted application code
        after compile_contract() has accepted the proposal against a trusted
        approved limit.

        A task_id may only be activated once in this MVP. Completed, revoked,
        or expired task identities cannot be reused.

        Raises:
            PolicyStoreError:
                If the policy, expiration, or lifecycle transition is invalid.
        """
        self._validate_policy(policy)

        now = self._now()
        normalized_expiry = self._validate_expiration(
            expires_at,
            now=now,
        )

        with self._lock:
            if policy.task_id in self._records:
                self._expire_if_needed(
                    self._records[policy.task_id],
                    now=now,
                )

                existing = self._records[policy.task_id].lifecycle

                raise PolicyStoreError(
                    "TASK_ALREADY_REGISTERED",
                    (
                        f"Task {policy.task_id!r} already has policy "
                        f"{existing.policy_id!r} in state "
                        f"{existing.state!r}."
                    ),
                )

            lifecycle = PolicyLifecycleRecord(
                task_id=policy.task_id,
                policy_id=policy.policy_id,
                state="ACTIVE",
                activated_at=now,
                expires_at=normalized_expiry,
                ended_at=None,
                end_reason=None,
            )

            self._records[policy.task_id] = _StoredPolicy(
                policy=policy,
                lifecycle=lifecycle,
            )

            return lifecycle

    def get_active(
        self,
        task_id: str,
    ) -> CompiledPolicy | None:
        """
        Return the trusted active policy for a task.

        Returns None when:
        - the task is unknown
        - the task is completed
        - the task is revoked
        - the task is expired

        Expiration is checked before the policy is returned.
        """
        validated_task_id = self._validate_task_id(task_id)
        now = self._now()

        with self._lock:
            stored = self._records.get(validated_task_id)

            if stored is None:
                return None

            self._expire_if_needed(stored, now=now)

            if stored.lifecycle.state != "ACTIVE":
                return None

            # CompiledPolicy and CompiledGrant are immutable snapshots.
            return stored.policy

    def status(
        self,
        task_id: str,
    ) -> PolicyLifecycleRecord:
        """
        Return the lifecycle record for a known task.

        Expiration is applied before the status is returned.

        Raises:
            KeyError:
                If the task has never been registered.
        """
        validated_task_id = self._validate_task_id(task_id)
        now = self._now()

        with self._lock:
            stored = self._records.get(validated_task_id)

            if stored is None:
                raise KeyError(
                    f"No policy lifecycle exists for task: "
                    f"{validated_task_id}"
                )

            self._expire_if_needed(stored, now=now)

            return stored.lifecycle

    def complete(
        self,
        task_id: str,
    ) -> PolicyLifecycleRecord:
        """
        Mark an ACTIVE task as successfully completed.

        After completion, get_active(task_id) returns None.
        """
        return self._end_task(
            task_id,
            target_state="COMPLETED",
            reason="task_completed",
        )

    def revoke(
        self,
        task_id: str,
        *,
        reason: str,
    ) -> PolicyLifecycleRecord:
        """
        Revoke an ACTIVE task policy.

        After revocation, get_active(task_id) returns None.
        """
        validated_reason = self._validate_revocation_reason(reason)

        return self._end_task(
            task_id,
            target_state="REVOKED",
            reason=validated_reason,
        )

    def records(self) -> tuple[PolicyLifecycleRecord, ...]:
        """
        Return lifecycle snapshots for all registered tasks.

        Expiration is applied before records are returned.
        """
        now = self._now()

        with self._lock:
            for stored in self._records.values():
                self._expire_if_needed(stored, now=now)

            return tuple(
                stored.lifecycle
                for _, stored in sorted(self._records.items())
            )

    def _end_task(
        self,
        task_id: str,
        *,
        target_state: Literal["COMPLETED", "REVOKED"],
        reason: str,
    ) -> PolicyLifecycleRecord:
        validated_task_id = self._validate_task_id(task_id)
        now = self._now()

        with self._lock:
            stored = self._records.get(validated_task_id)

            if stored is None:
                raise KeyError(
                    f"No policy lifecycle exists for task: "
                    f"{validated_task_id}"
                )

            self._expire_if_needed(stored, now=now)

            if stored.lifecycle.state != "ACTIVE":
                raise PolicyStoreError(
                    "TASK_NOT_ACTIVE",
                    (
                        f"Task {validated_task_id!r} is in state "
                        f"{stored.lifecycle.state!r}, not 'ACTIVE'."
                    ),
                )

            stored.lifecycle = replace(
                stored.lifecycle,
                state=target_state,
                ended_at=now,
                end_reason=reason,
            )

            return stored.lifecycle

    def _expire_if_needed(
        self,
        stored: _StoredPolicy,
        *,
        now: datetime,
    ) -> None:
        lifecycle = stored.lifecycle

        if lifecycle.state != "ACTIVE":
            return

        if lifecycle.expires_at is None:
            return

        if now < lifecycle.expires_at:
            return

        stored.lifecycle = replace(
            lifecycle,
            state="EXPIRED",
            ended_at=now,
            end_reason="policy_expired",
        )

    def _now(self) -> datetime:
        now = self._clock()

        if not isinstance(now, datetime):
            raise PolicyStoreError(
                "INVALID_CLOCK",
                "Policy store clock must return a datetime.",
            )

        if now.tzinfo is None or now.utcoffset() is None:
            raise PolicyStoreError(
                "INVALID_CLOCK",
                "Policy store clock must return a timezone-aware datetime.",
            )

        return now.astimezone(UTC)

    @staticmethod
    def _validate_policy(policy: CompiledPolicy) -> None:
        if not isinstance(policy, CompiledPolicy):
            raise PolicyStoreError(
                "INVALID_POLICY",
                "Only a CompiledPolicy can be activated.",
            )

        try:
            _TASK_ID_ADAPTER.validate_python(
                policy.task_id,
                strict=True,
            )
        except ValidationError as exc:
            raise PolicyStoreError(
                "INVALID_POLICY",
                "Compiled policy contains an invalid task_id.",
            ) from exc

        if (
            not isinstance(policy.policy_id, str)
            or len(policy.policy_id) != 64
            or any(
                character not in "0123456789abcdef"
                for character in policy.policy_id
            )
        ):
            raise PolicyStoreError(
                "INVALID_POLICY",
                "Compiled policy contains an invalid policy_id.",
            )

        if (
            not isinstance(policy.task, str)
            or not policy.task.strip()
        ):
            raise PolicyStoreError(
                "INVALID_POLICY",
                "Compiled policy contains invalid task text.",
            )

        if not isinstance(policy.allowed, tuple):
            raise PolicyStoreError(
                "INVALID_POLICY",
                "Compiled policy grants must be an immutable tuple.",
            )

    @staticmethod
    def _validate_expiration(
        expires_at: datetime | None,
        *,
        now: datetime,
    ) -> datetime | None:
        if expires_at is None:
            return None

        if not isinstance(expires_at, datetime):
            raise PolicyStoreError(
                "INVALID_EXPIRATION",
                "expires_at must be a datetime or None.",
            )

        if (
            expires_at.tzinfo is None
            or expires_at.utcoffset() is None
        ):
            raise PolicyStoreError(
                "INVALID_EXPIRATION",
                "expires_at must be timezone-aware.",
            )

        normalized = expires_at.astimezone(UTC)

        if normalized <= now:
            raise PolicyStoreError(
                "INVALID_EXPIRATION",
                "expires_at must be later than activation time.",
            )

        return normalized

    @staticmethod
    def _validate_task_id(task_id: str) -> str:
        try:
            return _TASK_ID_ADAPTER.validate_python(
                task_id,
                strict=True,
            )
        except ValidationError as exc:
            raise ValueError(
                "Invalid task_id."
            ) from exc

    @staticmethod
    def _validate_revocation_reason(reason: str) -> str:
        if not isinstance(reason, str):
            raise ValueError(
                "Revocation reason must be a string."
            )

        if not reason.strip():
            raise ValueError(
                "Revocation reason cannot be blank."
            )

        if reason != reason.strip():
            raise ValueError(
                "Revocation reason cannot contain surrounding whitespace."
            )

        if len(reason) > 500:
            raise ValueError(
                "Revocation reason cannot exceed 500 characters."
            )

        if any(not character.isprintable() for character in reason):
            raise ValueError(
                "Revocation reason cannot contain nonprintable characters."
            )

        return reason