from __future__ import annotations

from datetime import datetime
from threading import RLock

from app.policy.compiler import CompiledPolicy
from app.policy.runtime_snapshot import write_policy_snapshot
from app.policy.store import (
    ActivePolicyStore,
    PolicyLifecycleRecord,
)


class SnapshottingPolicyStore(
    ActivePolicyStore,
):
    """
    ActivePolicyStore with a sanitized runtime snapshot for observability.

    Security properties:

    - Authorization still uses the trusted in-memory ActivePolicyStore.
    - The snapshot is NOT used to authorize protected tool calls.
    - Only an already compiled policy is persisted.
    - The trusted approval ceiling is never persisted here.
    - Snapshot failures do not roll back or corrupt policy activation.

    The snapshot exists only so a separate read-only dashboard/API process
    can observe the policy that ToolFence actually activated.
    """

    def __init__(
        self,
        *,
        clock=None,
    ) -> None:
        super().__init__(
            clock=clock,
        )

        self._snapshot_lock = RLock()

        self._snapshot_policies: dict[
            str,
            CompiledPolicy,
        ] = {}

        self._snapshot_error: str | None = None

    @property
    def snapshot_error(
        self,
    ) -> str | None:
        """
        Return the most recent snapshot persistence error, if any.

        Snapshot persistence is observability-only and never determines
        whether authorization succeeds or fails.
        """

        with self._snapshot_lock:
            return self._snapshot_error

    def activate(
        self,
        policy: CompiledPolicy,
        *,
        expires_at: datetime | None = None,
    ) -> PolicyLifecycleRecord:
        lifecycle = super().activate(
            policy,
            expires_at=expires_at,
        )

        with self._snapshot_lock:
            self._snapshot_policies[
                policy.task_id
            ] = policy

        self._persist(
            policy,
            lifecycle,
        )

        return lifecycle

    def get_active(
        self,
        task_id: str,
    ) -> CompiledPolicy | None:
        policy = super().get_active(
            task_id
        )

        if policy is not None:
            return policy

        # get_active() may have changed an ACTIVE policy to EXPIRED.
        # Reflect that lifecycle change in the dashboard snapshot.
        known_policy = self._known_policy(
            task_id
        )

        if known_policy is not None:
            try:
                lifecycle = super().status(
                    task_id
                )
            except KeyError:
                return None

            self._persist(
                known_policy,
                lifecycle,
            )

        return None

    def status(
        self,
        task_id: str,
    ) -> PolicyLifecycleRecord:
        lifecycle = super().status(
            task_id
        )

        policy = self._known_policy(
            task_id
        )

        if policy is not None:
            self._persist(
                policy,
                lifecycle,
            )

        return lifecycle

    def complete(
        self,
        task_id: str,
    ) -> PolicyLifecycleRecord:
        lifecycle = super().complete(
            task_id
        )

        policy = self._known_policy(
            task_id
        )

        if policy is not None:
            self._persist(
                policy,
                lifecycle,
            )

        return lifecycle

    def revoke(
        self,
        task_id: str,
        *,
        reason: str,
    ) -> PolicyLifecycleRecord:
        lifecycle = super().revoke(
            task_id,
            reason=reason,
        )

        policy = self._known_policy(
            task_id
        )

        if policy is not None:
            self._persist(
                policy,
                lifecycle,
            )

        return lifecycle

    def records(
        self,
    ) -> tuple[
        PolicyLifecycleRecord,
        ...,
    ]:
        lifecycle_records = (
            super().records()
        )

        for lifecycle in lifecycle_records:
            policy = self._known_policy(
                lifecycle.task_id
            )

            if policy is not None:
                self._persist(
                    policy,
                    lifecycle,
                )

        return lifecycle_records

    def _known_policy(
        self,
        task_id: str,
    ) -> CompiledPolicy | None:
        with self._snapshot_lock:
            return self._snapshot_policies.get(
                task_id
            )

    def _persist(
        self,
        policy: CompiledPolicy,
        lifecycle: PolicyLifecycleRecord,
    ) -> None:
        """
        Best-effort observability persistence.

        A dashboard filesystem failure must never turn an already activated
        security policy into a misleading activation failure.
        """

        try:
            write_policy_snapshot(
                policy,
                state=lifecycle.state,
                activated_at=(
                    lifecycle.activated_at
                ),
                expires_at=(
                    lifecycle.expires_at
                ),
                ended_at=(
                    lifecycle.ended_at
                ),
                end_reason=(
                    lifecycle.end_reason
                ),
            )

        except (
            OSError,
            TypeError,
            ValueError,
        ) as exc:
            with self._snapshot_lock:
                self._snapshot_error = str(
                    exc
                )

            return

        with self._snapshot_lock:
            self._snapshot_error = None
