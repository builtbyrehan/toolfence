"""Regression tests for ToolFence's contract and authorization rules."""

from functools import partial
from pathlib import Path

import pytest

import app.policy.evaluator as evaluator
from app.policy.compiler import ContractValidationError, compile_contract
from app.policy.schema import CapabilityInventory, TaskCapabilityContract


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "BUG-17-FIX"
TASK_TEXT = "Fix BUG-17, run CI, and create a pull request"


@pytest.fixture(scope="module")
def inventory():
    return CapabilityInventory.model_validate_json(
        (PROJECT_ROOT / "config" / "capabilities.json").read_text(
            encoding="utf-8"
        )
    )


@pytest.fixture
def proposal():
    return {
        "task_id": TASK_ID,
        "task": TASK_TEXT,
        "allowed": [
            {"tool": "ticket.get", "resource": "BUG-17"},
            {"tool": "repo.read", "resource": "project/*"},
            {"tool": "repo.write", "resource": "project/src/*"},
            {"tool": "ci.run", "resource": "feature/BUG-17"},
            {"tool": "ci.status", "resource": "feature/BUG-17"},
            {
                "tool": "pull_request.create",
                "resource": "feature/BUG-17",
            },
        ],
    }


@pytest.fixture
def approved_limit(proposal):
    # A trusted test fixture, captured before a test changes the proposal.
    return TaskCapabilityContract.model_validate(proposal)


@pytest.fixture
def compile_proposal(inventory, approved_limit):
    return partial(
        compile_contract,
        inventory=inventory,
        approved_limit=approved_limit,
    )


@pytest.fixture
def policy(proposal, compile_proposal):
    return compile_proposal(proposal)


@pytest.mark.parametrize(
    "tool,resource,expected_code",
    [
        ("ticket.get", "BUG-17", "PERMITTED"),
        ("repo.read", "project/src/fix.py", "PERMITTED"),
        ("repo.read", "project/tests/test_fix.py", "PERMITTED"),
        ("repo.write", "project/src/fix.py", "PERMITTED"),
        ("repo.write", "project/src/lib/fix.py", "PERMITTED"),
        ("ci.run", "feature/BUG-17", "PERMITTED"),
        ("ci.status", "feature/BUG-17", "PERMITTED"),
        ("pull_request.create", "feature/BUG-17", "PERMITTED"),
        ("ticket.delete", "BUG-17", "TOOL_NOT_GRANTED"),
        ("release.deploy", "production", "TOOL_NOT_GRANTED"),
        ("secret.read", "production-key", "TOOL_NOT_GRANTED"),
        ("ticket.get", "BUG-18", "RESOURCE_OUT_OF_SCOPE"),
        ("repo.write", "project/tests/test_fix.py", "RESOURCE_OUT_OF_SCOPE"),
        ("repo.write", "project/src_backup/fix.py", "RESOURCE_OUT_OF_SCOPE"),
        ("repo.write", "other/src/fix.py", "RESOURCE_OUT_OF_SCOPE"),
        ("ci.run", "main", "RESOURCE_OUT_OF_SCOPE"),
        ("repo.write", "project/src/../secrets.txt", "INVALID_RESOURCE"),
        ("repo.write", r"project\src\fix.py", "INVALID_RESOURCE"),
        ("repo.write", "project/src/%2e%2e/secrets.txt", "INVALID_RESOURCE"),
        ("unknown.tool", "anything", "TOOL_NOT_GRANTED"),
    ],
)
def test_authorization_decisions(policy, tool, resource, expected_code):
    request = {"task_id": TASK_ID, "tool": tool, "resource": resource}

    first = evaluator.evaluate_call(policy, **request)
    second = evaluator.evaluate_call(policy, **request)

    expected_allowed = expected_code == "PERMITTED"
    assert first.allowed is expected_allowed
    assert first.decision == ("ALLOW" if expected_allowed else "DENY")
    assert first.reason_code == expected_code
    assert first.policy_id == policy.policy_id
    assert first.reason
    assert first == second


@pytest.mark.parametrize(
    "tool,resource,expected_code",
    [
        ("release.deploy", "production", "PERMISSION_EXCEEDS_APPROVAL"),
        ("repo.write", "project/*", "PERMISSION_EXCEEDS_APPROVAL"),
        ("ticket.get", "BUG-18", "PERMISSION_EXCEEDS_APPROVAL"),
        ("repo.delete", "project/src/fix.py", "UNKNOWN_TOOL"),
        ("repo.write", "project/src/../*", "INVALID_RESOURCE_SCOPE"),
        ("ci.run", "feature/*", "INVALID_RESOURCE_SCOPE"),
    ],
)
def test_rejects_unapproved_grants(
    proposal, compile_proposal, tool, resource, expected_code
):
    # One invalid addition must reject the whole proposal.
    proposal["allowed"].append({"tool": tool, "resource": resource})

    with pytest.raises(ContractValidationError) as caught:
        compile_proposal(proposal)

    assert caught.value.code == expected_code


@pytest.mark.parametrize(
    "field,value",
    [
        ("task_id", "BUG-18-FIX"),
        ("task", "Deploy the application to production"),
    ],
)
def test_compiler_requires_the_approved_task(
    proposal, compile_proposal, field, value
):
    proposal[field] = value

    with pytest.raises(ContractValidationError) as caught:
        compile_proposal(proposal)

    assert caught.value.code == "TASK_MISMATCH"


@pytest.mark.parametrize(
    "field,value",
    [
        ("task_id", 17),
        ("tool", b"repo.write"),
        ("resource", True),
        ("resource", ""),
    ],
)
def test_malformed_requests_are_denied(policy, field, value):
    request = {
        "task_id": TASK_ID,
        "tool": "repo.write",
        "resource": "project/src/fix.py",
    }
    request[field] = value

    result = evaluator.evaluate_call(policy, **request)

    assert not result.allowed
    assert result.reason_code == "INVALID_REQUEST"


def test_wrong_task_is_denied(policy):
    result = evaluator.evaluate_call(
        policy,
        task_id="BUG-18-FIX",
        tool="repo.write",
        resource="project/src/fix.py",
    )

    assert not result.allowed
    assert result.reason_code == "TASK_MISMATCH"


def test_missing_policy_is_denied():
    result = evaluator.evaluate_call(
        None,
        task_id=TASK_ID,
        tool="repo.write",
        resource="project/src/fix.py",
    )

    assert not result.allowed
    assert result.reason_code == "NO_ACTIVE_POLICY"


def test_empty_contract_grants_nothing(proposal, compile_proposal):
    proposal["allowed"] = []
    empty_policy = compile_proposal(proposal)

    result = evaluator.evaluate_call(
        empty_policy,
        task_id=TASK_ID,
        tool="ticket.get",
        resource="BUG-17",
    )

    assert empty_policy.allowed == ()
    assert not result.allowed
    assert result.reason_code == "TOOL_NOT_GRANTED"


def test_missing_permission_list_is_rejected(proposal, compile_proposal):
    del proposal["allowed"]

    with pytest.raises(ContractValidationError) as caught:
        compile_proposal(proposal)

    assert caught.value.code == "INVALID_CONTRACT"


def test_duplicate_grant_is_rejected(proposal, compile_proposal):
    proposal["allowed"].append(dict(proposal["allowed"][0]))

    with pytest.raises(ContractValidationError) as caught:
        compile_proposal(proposal)

    assert caught.value.code == "INVALID_CONTRACT"


def test_extra_contract_field_is_rejected(proposal, compile_proposal):
    proposal["admin"] = True

    with pytest.raises(ContractValidationError) as caught:
        compile_proposal(proposal)

    assert caught.value.code == "INVALID_CONTRACT"


def test_grant_order_does_not_change_policy(proposal, compile_proposal):
    original = compile_proposal(proposal)
    proposal["allowed"].reverse()
    reordered = compile_proposal(proposal)

    assert original == reordered


def test_input_changes_do_not_expand_compiled_policy(
    proposal, compile_proposal
):
    compiled = compile_proposal(proposal)

    for grant in proposal["allowed"]:
        if grant["tool"] == "repo.write":
            grant["resource"] = "project/*"

    result = evaluator.evaluate_call(
        compiled,
        task_id=TASK_ID,
        tool="repo.write",
        resource="project/private.txt",
    )

    assert not result.allowed
    assert result.reason_code == "RESOURCE_OUT_OF_SCOPE"


def test_internal_error_denies_the_call(policy, monkeypatch):
    def broken_matcher(*args, **kwargs):
        raise RuntimeError("forced test failure")

    monkeypatch.setattr(evaluator, "resource_matches", broken_matcher)

    result = evaluator.evaluate_call(
        policy,
        task_id=TASK_ID,
        tool="repo.write",
        resource="project/src/fix.py",
    )

    assert not result.allowed
    assert result.reason_code == "POLICY_ERROR"
    assert "forced test failure" not in result.reason