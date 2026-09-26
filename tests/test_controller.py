from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.policy.controller import (
    TaskControlError,
    TaskPolicyController,
    TrustedApprovalStore,
)
from app.policy.schema import (
    CapabilityInventory,
    TaskCapabilityContract,
)
from app.policy.store import ActivePolicyStore


TASK_ID = "BUG-17-FIX"

TASK = (
    "Fix BUG-17, run CI, and create a pull request."
)

BRANCH = "feature/BUG-17"


APPROVED = [
    {
        "tool": "ticket.get",
        "resource": "BUG-17",
    },
    {
        "tool": "repo.read",
        "resource": "project/*",
    },
    {
        "tool": "repo.write",
        "resource": "project/src/*",
    },
    {
        "tool": "ci.run",
        "resource": BRANCH,
    },
    {
        "tool": "ci.status",
        "resource": BRANCH,
    },
    {
        "tool": "pull_request.create",
        "resource": BRANCH,
    },
]


def _load_inventory() -> CapabilityInventory:
    raw = json.loads(
        Path(
            "config/capabilities.json"
        ).read_text(
            encoding="utf-8"
        )
    )

    return CapabilityInventory.model_validate(
        raw
    )


def _approval(
    *,
    task_id: str = TASK_ID,
    task: str = TASK,
    allowed: list[dict[str, str]] | None = None,
) -> TaskCapabilityContract:
    return TaskCapabilityContract.model_validate(
        {
            "task_id": task_id,
            "task": task,
            "allowed": (
                APPROVED
                if allowed is None
                else allowed
            ),
        }
    )


def _controller(
    *,
    approvals: TrustedApprovalStore | None = None,
    policy_store: ActivePolicyStore | None = None,
) -> tuple[
    TaskPolicyController,
    TrustedApprovalStore,
    ActivePolicyStore,
]:
    trusted_approvals = (
        approvals
        if approvals is not None
        else TrustedApprovalStore()
    )

    store = (
        policy_store
        if policy_store is not None
        else ActivePolicyStore()
    )

    controller = TaskPolicyController(
        inventory=_load_inventory(),
        approvals=trusted_approvals,
        policy_store=store,
    )

    return (
        controller,
        trusted_approvals,
        store,
    )


def test_proposal_without_trusted_approval_is_rejected() -> None:
    controller, _, policy_store = _controller()

    with pytest.raises(
        TaskControlError
    ) as exc_info:
        controller.submit_proposal(
            {
                "task_id": TASK_ID,
                "task": TASK,
                "allowed": APPROVED,
            }
        )

    assert (
        exc_info.value.code
        == "NO_TRUSTED_APPROVAL"
    )

    assert (
        policy_store.get_active(
            TASK_ID
        )
        is None
    )


def test_valid_proposal_is_compiled_and_activated() -> None:
    controller, approvals, policy_store = _controller()

    approvals.register(
        _approval()
    )

    result = controller.submit_proposal(
        {
            "task_id": TASK_ID,
            "task": TASK,
            "allowed": APPROVED,
        }
    )

    assert (
        result.policy.task_id
        == TASK_ID
    )

    assert (
        result.lifecycle.state
        == "ACTIVE"
    )

    assert (
        result.lifecycle.policy_id
        == result.policy.policy_id
    )

    active = policy_store.get_active(
        TASK_ID
    )

    assert active is not None

    assert (
        active.policy_id
        == result.policy.policy_id
    )

    assert len(active.allowed) == 6


def test_narrower_proposal_can_fit_inside_trusted_approval() -> None:
    controller, approvals, policy_store = _controller()

    approvals.register(
        _approval()
    )

    narrower = [
        {
            "tool": "ticket.get",
            "resource": "BUG-17",
        },
        {
            "tool": "repo.read",
            "resource": "project/src/*",
        },
    ]

    result = controller.submit_proposal(
        {
            "task_id": TASK_ID,
            "task": TASK,
            "allowed": narrower,
        }
    )

    assert (
        result.lifecycle.state
        == "ACTIVE"
    )

    assert len(
        result.policy.allowed
    ) == 2

    active = policy_store.get_active(
        TASK_ID
    )

    assert active is not None

    grants = {
        (
            grant.tool,
            grant.resource,
        )
        for grant in active.allowed
    }

    assert grants == {
        (
            "ticket.get",
            "BUG-17",
        ),
        (
            "repo.read",
            "project/src/*",
        ),
    }


def test_excess_permission_is_rejected() -> None:
    controller, approvals, policy_store = _controller()

    approvals.register(
        _approval()
    )

    excessive = [
        *APPROVED,
        {
            "tool": "secret.read",
            "resource": "production-key",
        },
    ]

    with pytest.raises(
        TaskControlError
    ) as exc_info:
        controller.submit_proposal(
            {
                "task_id": TASK_ID,
                "task": TASK,
                "allowed": excessive,
            }
        )

    assert (
        exc_info.value.code
        == "PERMISSION_EXCEEDS_APPROVAL"
    )

    assert (
        policy_store.get_active(
            TASK_ID
        )
        is None
    )


def test_broader_repository_scope_is_rejected() -> None:
    controller, approvals, policy_store = _controller()

    approvals.register(
        _approval()
    )

    broader = [
        {
            "tool": "ticket.get",
            "resource": "BUG-17",
        },
        {
            "tool": "repo.read",
            "resource": "project/*",
        },
        {
            "tool": "repo.write",
            "resource": "project/*",
        },
    ]

    with pytest.raises(
        TaskControlError
    ) as exc_info:
        controller.submit_proposal(
            {
                "task_id": TASK_ID,
                "task": TASK,
                "allowed": broader,
            }
        )

    assert (
        exc_info.value.code
        == "PERMISSION_EXCEEDS_APPROVAL"
    )

    assert (
        policy_store.get_active(
            TASK_ID
        )
        is None
    )


def test_proposal_cannot_change_approved_task_text() -> None:
    controller, approvals, policy_store = _controller()

    approvals.register(
        _approval()
    )

    with pytest.raises(
        TaskControlError
    ) as exc_info:
        controller.submit_proposal(
            {
                "task_id": TASK_ID,
                "task": (
                    "Deploy the application "
                    "to production."
                ),
                "allowed": APPROVED,
            }
        )

    assert (
        exc_info.value.code
        == "TASK_MISMATCH"
    )

    assert (
        policy_store.get_active(
            TASK_ID
        )
        is None
    )


def test_trusted_approval_cannot_be_replaced() -> None:
    approvals = TrustedApprovalStore()

    first = approvals.register(
        _approval()
    )

    assert (
        approvals.get(TASK_ID)
        is first
    )

    with pytest.raises(
        TaskControlError
    ) as exc_info:
        approvals.register(
            _approval()
        )

    assert (
        exc_info.value.code
        == "APPROVAL_ALREADY_REGISTERED"
    )

    assert (
        approvals.get(TASK_ID)
        is first
    )


def test_second_activation_for_same_task_is_rejected() -> None:
    controller, approvals, policy_store = _controller()

    approvals.register(
        _approval()
    )

    first = controller.submit_proposal(
        {
            "task_id": TASK_ID,
            "task": TASK,
            "allowed": APPROVED,
        }
    )

    assert (
        first.lifecycle.state
        == "ACTIVE"
    )

    with pytest.raises(
        TaskControlError
    ) as exc_info:
        controller.submit_proposal(
            {
                "task_id": TASK_ID,
                "task": TASK,
                "allowed": APPROVED,
            }
        )

    assert (
        exc_info.value.code
        == "TASK_ALREADY_REGISTERED"
    )

    active = policy_store.get_active(
        TASK_ID
    )

    assert active is not None

    assert (
        active.policy_id
        == first.policy.policy_id
    )


def test_empty_proposal_is_valid_when_within_approval() -> None:
    controller, approvals, policy_store = _controller()

    approvals.register(
        _approval()
    )

    result = controller.submit_proposal(
        {
            "task_id": TASK_ID,
            "task": TASK,
            "allowed": [],
        }
    )

    assert (
        result.lifecycle.state
        == "ACTIVE"
    )

    assert (
        result.policy.allowed
        == ()
    )

    active = policy_store.get_active(
        TASK_ID
    )

    assert active is not None
    assert active.allowed == ()


def test_invalid_proposal_does_not_create_policy() -> None:
    controller, approvals, policy_store = _controller()

    approvals.register(
        _approval()
    )

    with pytest.raises(
        TaskControlError
    ) as exc_info:
        controller.submit_proposal(
            {
                "task_id": TASK_ID,
                "task": TASK,
                # required "allowed" field is intentionally missing
            }
        )

    assert (
        exc_info.value.code
        == "INVALID_CONTRACT"
    )

    assert (
        policy_store.get_active(
            TASK_ID
        )
        is None
    )