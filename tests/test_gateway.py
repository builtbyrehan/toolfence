from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pytest

from app.gateway.audit import AuditLog
from app.gateway.dispatcher import ProtectedToolDispatcher
from app.policy.compiler import CompiledPolicy, compile_contract
from app.policy.schema import (
    CapabilityInventory,
    TaskCapabilityContract,
)
from app.policy.store import ActivePolicyStore
from mock_mcp.ci import CIService
from mock_mcp.release import ReleaseService
from mock_mcp.repository import RepositoryService
from mock_mcp.secrets import SecretService
from mock_mcp.tickets import TicketService


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


@dataclass
class GatewayHarness:
    policy: CompiledPolicy
    store: ActivePolicyStore
    audit: AuditLog

    tickets: TicketService
    repository: RepositoryService
    ci: CIService
    release: ReleaseService
    secrets: SecretService

    dispatcher: ProtectedToolDispatcher


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


def _compile_policy() -> CompiledPolicy:
    inventory = _load_inventory()

    approved_limit = (
        TaskCapabilityContract.model_validate(
            {
                "task_id": TASK_ID,
                "task": TASK,
                "allowed": ALLOWED,
            }
        )
    )

    proposal = {
        "task_id": TASK_ID,
        "task": TASK,
        "allowed": ALLOWED,
    }

    return compile_contract(
        proposal,
        inventory=inventory,
        approved_limit=approved_limit,
    )


def _build_harness(
    tmp_path: Path,
    *,
    activate_policy: bool = True,
) -> GatewayHarness:
    policy = _compile_policy()

    store = ActivePolicyStore()

    if activate_policy:
        store.activate(policy)

    audit = AuditLog(
        tmp_path / "audit.jsonl"
    )

    tickets = TicketService()

    repository = RepositoryService()

    # Important:
    # CI receives the same repository instance used by repo.read/write.
    ci = CIService(repository)

    release = ReleaseService()

    secrets = SecretService()

    dispatcher = ProtectedToolDispatcher(
        policy_store=store,
        audit=audit,
        tickets=tickets,
        repository=repository,
        ci=ci,
        release=release,
        secrets=secrets,
    )

    return GatewayHarness(
        policy=policy,
        store=store,
        audit=audit,
        tickets=tickets,
        repository=repository,
        ci=ci,
        release=release,
        secrets=secrets,
        dispatcher=dispatcher,
    )


@pytest.fixture
def gateway(
    tmp_path: Path,
) -> GatewayHarness:
    return _build_harness(tmp_path)


def test_allowed_ticket_get_executes_and_is_audited(
    gateway: GatewayHarness,
) -> None:
    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ticket.get",
        arguments={
            "ticket_id": "BUG-17",
        },
    )

    assert result.decision == "ALLOW"
    assert result.reason_code == "PERMITTED"

    assert (
        result.execution_status
        == "SUCCEEDED"
    )

    assert result.result is not None
    assert result.result["ticket_id"] == "BUG-17"

    assert result.audit_event_id == 1
    assert result.audit_error_code is None

    events = gateway.audit.events(
        task_id=TASK_ID
    )

    assert len(events) == 1

    event = events[0]

    assert event.tool == "ticket.get"
    assert event.resource == "BUG-17"
    assert event.decision == "ALLOW"

    assert (
        event.execution_status
        == "SUCCEEDED"
    )


def test_secret_read_is_denied_and_audited(
    gateway: GatewayHarness,
) -> None:
    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="secret.read",
        arguments={
            "secret_id": "production-key",
        },
    )

    assert result.decision == "DENY"

    assert (
        result.reason_code
        == "TOOL_NOT_GRANTED"
    )

    assert (
        result.execution_status
        == "NOT_EXECUTED"
    )

    assert result.result is None
    assert result.audit_event_id == 1

    events = gateway.audit.events()

    assert len(events) == 1
    assert events[0].tool == "secret.read"
    assert events[0].decision == "DENY"

    audit_text = (
        gateway.audit.path.read_text(
            encoding="utf-8"
        )
    )

    # Secret values must never appear in the audit trail.
    assert (
        "DEMO_ONLY_NOT_A_REAL_PRODUCTION_SECRET"
        not in audit_text
    )

    # Backend response payloads are not persisted.
    assert '"result"' not in audit_text


def test_release_deploy_denial_does_not_change_state(
    gateway: GatewayHarness,
) -> None:
    before = gateway.release.status(
        "production"
    )

    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="release.deploy",
        arguments={
            "environment": "production",
            "version": "dangerous-2.0.0",
        },
    )

    assert result.decision == "DENY"

    assert (
        result.execution_status
        == "NOT_EXECUTED"
    )

    after = gateway.release.status(
        "production"
    )

    assert (
        after["deployed_version"]
        == before["deployed_version"]
    )

    assert after["deployment_count"] == 0

    assert (
        gateway.release.deployment_history()
        == []
    )


def test_out_of_scope_repo_write_is_not_executed(
    gateway: GatewayHarness,
) -> None:
    forbidden_path = (
        "project/tests/evil.py"
    )

    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="repo.write",
        arguments={
            "path": forbidden_path,
            "content": (
                "print('should never run')\n"
            ),
        },
    )

    assert result.decision == "DENY"

    assert (
        result.reason_code
        == "RESOURCE_OUT_OF_SCOPE"
    )

    assert (
        result.execution_status
        == "NOT_EXECUTED"
    )

    with pytest.raises(KeyError):
        gateway.repository.read(
            forbidden_path
        )

    event = gateway.audit.events()[0]

    assert event.resource == forbidden_path
    assert event.decision == "DENY"


def test_repo_write_changes_the_state_seen_by_ci(
    gateway: GatewayHarness,
) -> None:
    first_ci = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ci.run",
        arguments={
            "branch": BRANCH,
        },
    )

    assert first_ci.decision == "ALLOW"

    assert (
        first_ci.execution_status
        == "SUCCEEDED"
    )

    assert (
        first_ci.result["status"]
        == "FAILED"
    )

    write = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="repo.write",
        arguments={
            "path": SOURCE_PATH,
            "content": FIXED_SOURCE,
        },
    )

    assert write.decision == "ALLOW"

    assert (
        write.execution_status
        == "SUCCEEDED"
    )

    assert (
        gateway.repository.read(
            SOURCE_PATH
        )["content"]
        == FIXED_SOURCE
    )

    second_ci = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ci.run",
        arguments={
            "branch": BRANCH,
        },
    )

    assert second_ci.decision == "ALLOW"

    assert (
        second_ci.execution_status
        == "SUCCEEDED"
    )

    assert (
        second_ci.result["status"]
        == "PASSED"
    )

    events = gateway.audit.events()

    assert len(events) == 3

    assert [
        event.tool
        for event in events
    ] == [
        "ci.run",
        "repo.write",
        "ci.run",
    ]


def test_pull_request_creation_records_the_fix(
    gateway: GatewayHarness,
) -> None:
    write = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="repo.write",
        arguments={
            "path": SOURCE_PATH,
            "content": FIXED_SOURCE,
        },
    )

    assert write.succeeded

    result = gateway.dispatcher.dispatch(
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

    assert result.decision == "ALLOW"
    assert result.succeeded

    assert result.result["number"] == 1
    assert result.result["branch"] == BRANCH

    assert (
        SOURCE_PATH
        in result.result["changed_files"]
    )

    assert (
        result.result["changes"][SOURCE_PATH]
        == FIXED_SOURCE
    )


def test_authorized_backend_failure_is_recorded_separately(
    gateway: GatewayHarness,
) -> None:
    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="repo.read",
        arguments={
            "path": (
                "project/src/missing.py"
            ),
        },
    )

    # Authorization succeeded.
    assert result.decision == "ALLOW"
    assert result.reason_code == "PERMITTED"

    # Backend execution failed.
    assert (
        result.execution_status
        == "FAILED"
    )

    assert (
        result.execution_error_code
        == "BACKEND_REJECTED"
    )

    assert result.audit_event_id == 1

    event = gateway.audit.events()[0]

    assert event.decision == "ALLOW"

    assert (
        event.execution_status
        == "FAILED"
    )

    assert (
        event.execution_error_code
        == "BACKEND_REJECTED"
    )


def test_completed_task_has_no_active_policy(
    gateway: GatewayHarness,
) -> None:
    completed = gateway.store.complete(
        TASK_ID
    )

    assert completed.state == "COMPLETED"

    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ticket.get",
        arguments={
            "ticket_id": "BUG-17",
        },
    )

    assert result.decision == "DENY"

    assert (
        result.reason_code
        == "NO_ACTIVE_POLICY"
    )

    assert (
        result.execution_status
        == "NOT_EXECUTED"
    )

    assert result.audit_event_id == 1


def test_missing_active_policy_denies_by_default(
    tmp_path: Path,
) -> None:
    gateway = _build_harness(
        tmp_path,
        activate_policy=False,
    )

    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ticket.get",
        arguments={
            "ticket_id": "BUG-17",
        },
    )

    assert result.decision == "DENY"

    assert (
        result.reason_code
        == "NO_ACTIVE_POLICY"
    )

    assert (
        result.execution_status
        == "NOT_EXECUTED"
    )

    assert (
        gateway.audit.events()[0].decision
        == "DENY"
    )


def test_invalid_extra_argument_fails_closed(
    gateway: GatewayHarness,
) -> None:
    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ticket.get",
        arguments={
            "ticket_id": "BUG-17",
            "unexpected": "value",
        },
    )

    assert result.decision == "DENY"

    assert (
        result.reason_code
        == "INVALID_ARGUMENTS"
    )

    assert (
        result.execution_status
        == "NOT_EXECUTED"
    )

    assert result.result is None


def test_unknown_tool_fails_closed(
    gateway: GatewayHarness,
) -> None:
    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="unknown.tool",
        arguments={},
    )

    assert result.decision == "DENY"

    assert (
        result.reason_code
        == "UNKNOWN_TOOL"
    )

    assert (
        result.execution_status
        == "NOT_EXECUTED"
    )

    assert result.result is None


def test_denied_ticket_delete_does_not_delete_ticket(
    gateway: GatewayHarness,
) -> None:
    result = gateway.dispatcher.dispatch(
        task_id=TASK_ID,
        tool="ticket.delete",
        arguments={
            "ticket_id": "BUG-17",
        },
    )

    assert result.decision == "DENY"

    assert (
        result.reason_code
        == "TOOL_NOT_GRANTED"
    )

    assert (
        result.execution_status
        == "NOT_EXECUTED"
    )

    # Verify the denied destructive action never reached the backend.
    ticket = gateway.tickets.get(
        "BUG-17"
    )

    assert ticket["ticket_id"] == "BUG-17"

    event = gateway.audit.events()[0]

    assert event.tool == "ticket.delete"
    assert event.decision == "DENY"