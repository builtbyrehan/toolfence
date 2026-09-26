from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from threading import RLock

from pydantic import ValidationError

from app.policy.compiler import (
    CompiledPolicy,
    ContractValidationError,
    compile_contract,
)
from app.policy.schema import (
    CapabilityInventory,
    TaskCapabilityContract,
)
from app.policy.store import (
    ActivePolicyStore,
    PolicyLifecycleRecord,
    PolicyStoreError,
)


class TaskControlError(ValueError):
    """
    Raised when the trusted task-control workflow cannot proceed.

    Attributes:
        code:
            Stable machine-readable error code.

        message:
            Human-readable explanation.
    """

    def __init__(
        self,
        code: str,
        message: str,
    ) -> None:
        self.code = code
        self.message = message

        super().__init__(
            f"{code}: {message}"
        )


class TrustedApprovalStore:
    """
    In-memory store of developer/application-approved permission limits.

    This store belongs to the trusted control plane.

    Bob may propose a Task Capability Contract, but Bob-facing code must not
    be able to provide or replace the approval used to validate that proposal.

    An approval is immutable for a task_id in this MVP. If the approved
    permission boundary needs to change, create a new task identity instead
    of silently replacing the existing approval.
    """

    def __init__(self) -> None:
        self._lock = RLock()

        self._approvals: dict[
            str,
            TaskCapabilityContract,
        ] = {}

    def register(
        self,
        approval: TaskCapabilityContract,
    ) -> TaskCapabilityContract:
        """
        Register one trusted approval limit.

        The approval is strictly revalidated before storage.

        Raises:
            TaskControlError:
                If the approval is invalid or an approval already exists for
                this task_id.
        """

        try:
            validated = (
                TaskCapabilityContract
                .model_validate(
                    approval,
                    strict=True,
                )
            )

        except ValidationError as exc:
            raise TaskControlError(
                "INVALID_APPROVAL",
                (
                    "Trusted approval failed "
                    "schema validation."
                ),
            ) from exc

        with self._lock:
            if validated.task_id in self._approvals:
                raise TaskControlError(
                    "APPROVAL_ALREADY_REGISTERED",
                    (
                        "An approval already exists for task "
                        f"{validated.task_id!r}."
                    ),
                )

            self._approvals[
                validated.task_id
            ] = validated

            return validated

    def get(
        self,
        task_id: str,
    ) -> TaskCapabilityContract | None:
        """
        Return the trusted approval for a task, or None if none exists.
        """

        if not isinstance(task_id, str):
            raise TypeError(
                "task_id must be a string."
            )

        with self._lock:
            return self._approvals.get(
                task_id
            )

    def approvals(
        self,
    ) -> tuple[TaskCapabilityContract, ...]:
        """
        Return registered approvals ordered by task_id.
        """

        with self._lock:
            return tuple(
                self._approvals[task_id]
                for task_id in sorted(
                    self._approvals
                )
            )


@dataclass(frozen=True, slots=True)
class PolicyActivationResult:
    """
    Result of successfully compiling and activating a Bob proposal.
    """

    policy: CompiledPolicy
    lifecycle: PolicyLifecycleRecord


class TaskPolicyController:
    """
    Trusted control-plane workflow for task-policy activation.

    The key security property is that submit_proposal() accepts only the
    Bob/application proposal.

    It does NOT accept an approved_limit parameter.

    Instead, the controller retrieves the separately registered trusted
    approval from TrustedApprovalStore and validates the proposal against it.
    """

    def __init__(
        self,
        *,
        inventory: CapabilityInventory,
        approvals: TrustedApprovalStore,
        policy_store: ActivePolicyStore,
    ) -> None:
        try:
            validated_inventory = (
                CapabilityInventory
                .model_validate(
                    inventory,
                    strict=True,
                )
            )

        except ValidationError as exc:
            raise TaskControlError(
                "INVALID_INVENTORY",
                (
                    "Capability inventory failed "
                    "schema validation."
                ),
            ) from exc

        if not isinstance(
            approvals,
            TrustedApprovalStore,
        ):
            raise TypeError(
                "approvals must be a "
                "TrustedApprovalStore."
            )

        if not isinstance(
            policy_store,
            ActivePolicyStore,
        ):
            raise TypeError(
                "policy_store must be an "
                "ActivePolicyStore."
            )

        self._inventory = validated_inventory
        self._approvals = approvals
        self._policy_store = policy_store

    def submit_proposal(
        self,
        proposal: (
            TaskCapabilityContract
            | dict[str, object]
        ),
        *,
        expires_at: datetime | None = None,
    ) -> PolicyActivationResult:
        """
        Validate a proposed Task Capability Contract against the separately
        stored trusted approval, compile it, and activate it.

        The caller cannot provide the approval to this method.

        Raises:
            TaskControlError:
                If the proposal is malformed, no trusted approval exists,
                compilation fails, or activation fails.
        """

        proposed_contract = (
            self._validate_proposal(
                proposal
            )
        )

        approved_limit = (
            self._approvals.get(
                proposed_contract.task_id
            )
        )

        if approved_limit is None:
            raise TaskControlError(
                "NO_TRUSTED_APPROVAL",
                (
                    "No trusted approval is registered "
                    f"for task "
                    f"{proposed_contract.task_id!r}."
                ),
            )

        try:
            policy = compile_contract(
                proposed_contract,
                inventory=self._inventory,
                approved_limit=approved_limit,
            )

        except ContractValidationError as exc:
            raise TaskControlError(
                exc.code,
                exc.message,
            ) from exc

        try:
            lifecycle = (
                self._policy_store.activate(
                    policy,
                    expires_at=expires_at,
                )
            )

        except PolicyStoreError as exc:
            raise TaskControlError(
                exc.code,
                exc.message,
            ) from exc

        return PolicyActivationResult(
            policy=policy,
            lifecycle=lifecycle,
        )

    @staticmethod
    def _validate_proposal(
        proposal: (
            TaskCapabilityContract
            | dict[str, object]
        ),
    ) -> TaskCapabilityContract:
        try:
            return (
                TaskCapabilityContract
                .model_validate(
                    proposal,
                    strict=True,
                )
            )

        except ValidationError as exc:
            raise TaskControlError(
                "INVALID_CONTRACT",
                (
                    "Proposed task capability contract "
                    "failed schema validation."
                ),
            ) from exc