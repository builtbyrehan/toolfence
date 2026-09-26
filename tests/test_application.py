from __future__ import annotations

from pathlib import Path

import pytest

from app.application import create_application
from app.policy.controller import TaskControlError
from app.policy.schema import TaskCapabilityContract


TASK_ID = "BUG-17-FIX"

TASK = (
    "Fix BUG-17, run CI, and create a pull request."
)

BRANCH = "feature/BUG-17"

SOURCE_PATH = "project/src/cart.py"


ALLOWED = [
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


FIXED_SOURCE = (
    "def calculate_total(prices):\n"
    "    return sum(prices)\n"
)


def _trusted_approval() -> TaskCapabilityContract:
    return TaskCapabilityContract.model_validate(
        {
            "task_id": TASK_ID,
            "task": TASK,
            "allowed": ALLOWED,
        }
    )


def _proposal() -> dict[str, object]:
    return {
        "task_id": TASK_ID,
        "task": TASK,
        "allowed": ALLOWED,
    }


def test_application_loads_trusted_capability_inventory(
    tmp_path: Path,
) -> None:
    app = create_application(
        audit_path=tmp_path / "audit.jsonl"
    )

    assert len(app.inventory.capabilities) == 11

    tool_names = {
        capability.tool
        for capability in app.inventory.capabilities
    }

    assert "ticket.get" in tool_names
    assert "repo.read" in tool_names
    assert "repo.write" in tool_names
    assert "ci.run" in tool_names
    assert "release.deploy" in tool_names
    assert "secret.read" in tool_names


def test_fresh_application_has_no_approval_or_active_policy(
    tmp_path: Path,
) -> None:
    app = create_application(
        audit_path=tmp_path / "audit.jsonl"
    )

    assert app.approvals.approvals() == ()

    assert (
        app.policy_store.get_active(TASK_ID)
        is None
    )


def test_proposal_cannot_activate_without_trusted_approval(
    tmp_path: Path,
) -> None:
    app = create_application(
        audit_path=tmp_path / "audit.jsonl"
    )

    with pytest.raises(
        TaskControlError
    ) as exc_info:
        app.controller.submit_proposal(
            _proposal()
        )

    assert (
        exc_info.value.code
        == "NO_TRUSTED_APPROVAL"
    )

    assert (
        app.policy_store.get_active(TASK_ID)
        is None
    )


def test_trusted_approval_then_proposal_activates_policy(
    tmp_path: Path,
) -> None:
    app = create_application(
        audit_path=tmp_path / "audit.jsonl"
    )

    app.approvals.register(
        _trusted_approval()
    )

    activation = (
        app.controller.submit_proposal(
            _proposal()
        )
    )

    assert (
        activation.lifecycle.state
        == "ACTIVE"
    )

    assert (
        activation.policy.task_id
        == TASK_ID
    )

    assert len(
        activation.policy.allowed
    ) == 6

    active = app.policy_store.get_active(
        TASK_ID
    )

    assert active is not None

    assert (
        active.policy_id
        == activation.policy.policy_id
    )


def test_allowed_and_denied_actions_flow_through_same_application(
    tmp_path: Path,
) -> None:
    app = create_application(
        audit_path=tmp_path / "audit.jsonl"
    )

    app.approvals.register(
        _trusted_approval()
    )

    app.controller.submit_proposal(
        _proposal()
    )

    ticket = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ticket.get",
        arguments={
            "ticket_id": "BUG-17",
        },
    )

    assert ticket.decision == "ALLOW"
    assert ticket.succeeded

    secret = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="secret.read",
        arguments={
            "secret_id": "production-key",
        },
    )

    assert secret.decision == "DENY"

    assert (
        secret.reason_code
        == "TOOL_NOT_GRANTED"
    )

    assert (
        secret.execution_status
        == "NOT_EXECUTED"
    )

    events = app.audit.events(
        task_id=TASK_ID
    )

    assert len(events) == 2

    assert events[0].tool == "ticket.get"
    assert events[0].decision == "ALLOW"

    assert events[1].tool == "secret.read"
    assert events[1].decision == "DENY"


def test_repository_fix_changes_ci_result(
    tmp_path: Path,
) -> None:
    app = create_application(
        audit_path=tmp_path / "audit.jsonl"
    )

    app.approvals.register(
        _trusted_approval()
    )

    app.controller.submit_proposal(
        _proposal()
    )

    first_ci = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ci.run",
        arguments={
            "branch": BRANCH,
        },
    )

    assert first_ci.decision == "ALLOW"
    assert first_ci.succeeded

    assert (
        first_ci.result["status"]
        == "FAILED"
    )

    write = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="repo.write",
        arguments={
            "path": SOURCE_PATH,
            "content": FIXED_SOURCE,
        },
    )

    assert write.decision == "ALLOW"
    assert write.succeeded

    stored_source = app.repository.read(
        SOURCE_PATH
    )

    assert (
        stored_source["content"]
        == FIXED_SOURCE
    )

    second_ci = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ci.run",
        arguments={
            "branch": BRANCH,
        },
    )

    assert second_ci.decision == "ALLOW"
    assert second_ci.succeeded

    assert (
        second_ci.result["status"]
        == "PASSED"
    )

    events = app.audit.events(
        task_id=TASK_ID
    )

    assert [
        event.tool
        for event in events
    ] == [
        "ci.run",
        "repo.write",
        "ci.run",
    ]


def test_golden_task_can_fix_ci_and_create_pull_request(
    tmp_path: Path,
) -> None:
    app = create_application(
        audit_path=tmp_path / "audit.jsonl"
    )

    app.approvals.register(
        _trusted_approval()
    )

    app.controller.submit_proposal(
        _proposal()
    )

    ticket = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ticket.get",
        arguments={
            "ticket_id": "BUG-17",
        },
    )

    assert ticket.succeeded

    initial_ci = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ci.run",
        arguments={
            "branch": BRANCH,
        },
    )

    assert (
        initial_ci.result["status"]
        == "FAILED"
    )

    write = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="repo.write",
        arguments={
            "path": SOURCE_PATH,
            "content": FIXED_SOURCE,
        },
    )

    assert write.succeeded

    fixed_ci = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ci.run",
        arguments={
            "branch": BRANCH,
        },
    )

    assert (
        fixed_ci.result["status"]
        == "PASSED"
    )

    pr = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="pull_request.create",
        arguments={
            "branch": BRANCH,
            "title": "Fix BUG-17 cart total",
            "body": (
                "Include every cart item when "
                "calculating the total."
            ),
        },
    )

    assert pr.decision == "ALLOW"
    assert pr.succeeded

    assert pr.result["number"] == 1

    assert (
        SOURCE_PATH
        in pr.result["changed_files"]
    )

    assert (
        pr.result["changes"][SOURCE_PATH]
        == FIXED_SOURCE
    )

    events = app.audit.events(
        task_id=TASK_ID
    )

    assert len(events) == 5

    assert [
        event.tool
        for event in events
    ] == [
        "ticket.get",
        "ci.run",
        "repo.write",
        "ci.run",
        "pull_request.create",
    ]

    assert all(
        event.decision == "ALLOW"
        for event in events
    )


def test_forbidden_actions_do_not_mutate_backends(
    tmp_path: Path,
) -> None:
    app = create_application(
        audit_path=tmp_path / "audit.jsonl"
    )

    app.approvals.register(
        _trusted_approval()
    )

    app.controller.submit_proposal(
        _proposal()
    )

    production_before = app.release.status(
        "production"
    )

    deploy = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="release.deploy",
        arguments={
            "environment": "production",
            "version": "dangerous-2.0.0",
        },
    )

    assert deploy.decision == "DENY"

    assert (
        deploy.execution_status
        == "NOT_EXECUTED"
    )

    production_after = app.release.status(
        "production"
    )

    assert (
        production_after
        == production_before
    )

    delete_ticket = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ticket.delete",
        arguments={
            "ticket_id": "BUG-17",
        },
    )

    assert (
        delete_ticket.decision
        == "DENY"
    )

    assert (
        delete_ticket.execution_status
        == "NOT_EXECUTED"
    )

    # Ticket must still exist.
    assert (
        app.tickets.get(
            "BUG-17"
        )["ticket_id"]
        == "BUG-17"
    )

    events = app.audit.events(
        task_id=TASK_ID
    )

    assert len(events) == 2

    assert all(
        event.decision == "DENY"
        for event in events
    )


def test_completed_task_can_no_longer_use_tools(
    tmp_path: Path,
) -> None:
    app = create_application(
        audit_path=tmp_path / "audit.jsonl"
    )

    app.approvals.register(
        _trusted_approval()
    )

    app.controller.submit_proposal(
        _proposal()
    )

    before_completion = (
        app.dispatcher.dispatch(
            task_id=TASK_ID,
            tool="ticket.get",
            arguments={
                "ticket_id": "BUG-17",
            },
        )
    )

    assert before_completion.succeeded

    completed = app.policy_store.complete(
        TASK_ID
    )

    assert (
        completed.state
        == "COMPLETED"
    )

    after_completion = (
        app.dispatcher.dispatch(
            task_id=TASK_ID,
            tool="ticket.get",
            arguments={
                "ticket_id": "BUG-17",
            },
        )
    )

    assert (
        after_completion.decision
        == "DENY"
    )

    assert (
        after_completion.reason_code
        == "NO_ACTIVE_POLICY"
    )

    assert (
        after_completion.execution_status
        == "NOT_EXECUTED"
    )

    events = app.audit.events(
        task_id=TASK_ID
    )

    assert len(events) == 2

    assert events[0].decision == "ALLOW"
    assert events[1].decision == "DENY"


def test_audit_file_contains_no_secret_backend_value(
    tmp_path: Path,
) -> None:
    audit_path = (
        tmp_path
        / "audit.jsonl"
    )

    app = create_application(
        audit_path=audit_path
    )

    app.approvals.register(
        _trusted_approval()
    )

    app.controller.submit_proposal(
        _proposal()
    )

    result = app.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="secret.read",
        arguments={
            "secret_id": "production-key",
        },
    )

    assert result.decision == "DENY"

    audit_text = audit_path.read_text(
        encoding="utf-8"
    )

    assert (
        "DEMO_ONLY_NOT_A_REAL_PRODUCTION_SECRET"
        not in audit_text
    )

    assert '"result"' not in audit_text