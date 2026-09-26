"""Validate task proposals and compile deterministic policy snapshots."""

from dataclasses import asdict, dataclass
from hashlib import sha256
import json

from pydantic import ValidationError

from app.policy.matcher import scope_covers, validate_resource_pattern
from app.policy.schema import (
    CapabilityDefinition,
    CapabilityInventory,
    ResourceType,
    TaskCapabilityContract,
)


class ContractValidationError(ValueError):
    """A rejected contract or configuration, with a stable reason code."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True, slots=True)
class CompiledGrant:
    tool: str
    resource: str
    resource_type: ResourceType


@dataclass(frozen=True, slots=True)
class CompiledPolicy:
    """Immutable policy content; activation is handled separately."""

    policy_id: str
    task_id: str
    task: str
    allowed: tuple[CompiledGrant, ...]


def _check_grants(
    contract: TaskCapabilityContract,
    tools: dict[str, CapabilityDefinition],
    label: str,
) -> None:
    for grant in contract.allowed:
        capability = tools.get(grant.tool)

        if capability is None:
            raise ContractValidationError(
                "UNKNOWN_TOOL",
                f"{label} references an unknown tool: {grant.tool}",
            )

        try:
            validate_resource_pattern(
                capability.resource_type,
                grant.resource,
            )
        except ValueError as exc:
            raise ContractValidationError(
                "INVALID_RESOURCE_SCOPE",
                f"{label} has an invalid scope for {grant.tool}: {exc}",
            ) from exc


def compile_contract(
    proposal: TaskCapabilityContract | dict[str, object],
    *,
    inventory: CapabilityInventory,
    approved_limit: TaskCapabilityContract,
) -> CompiledPolicy:
    """Compile a proposal inside a trusted, task-specific approval limit.

    The inventory and approved limit must come from developer-controlled
    configuration. They must not be supplied by Bob with its proposal.
    """
    try:
        catalog = CapabilityInventory.model_validate(inventory)
    except ValidationError as exc:
        raise ContractValidationError(
            "INVALID_INVENTORY",
            "The capability inventory failed schema validation.",
        ) from exc

    try:
        approval = TaskCapabilityContract.model_validate(approved_limit)
    except ValidationError as exc:
        raise ContractValidationError(
            "INVALID_APPROVAL",
            "The approved limit failed schema validation.",
        ) from exc

    try:
        contract = TaskCapabilityContract.model_validate(proposal)
    except ValidationError as exc:
        raise ContractValidationError(
            "INVALID_CONTRACT",
            "The proposed contract failed schema validation.",
        ) from exc

    if contract.task_id != approval.task_id or contract.task != approval.task:
        raise ContractValidationError(
            "TASK_MISMATCH",
            "The proposal must preserve the approved task ID and task text.",
        )

    tools = {capability.tool: capability for capability in catalog.capabilities}

    # Validate both documents before considering any proposed permission.
    _check_grants(approval, tools, "Approved limit")
    _check_grants(contract, tools, "Proposal")

    for grant in contract.allowed:
        resource_type = tools[grant.tool].resource_type

        within_limit = any(
            approved.tool == grant.tool
            and scope_covers(
                resource_type,
                approved.resource,
                grant.resource,
            )
            for approved in approval.allowed
        )

        if not within_limit:
            raise ContractValidationError(
                "PERMISSION_EXCEEDS_APPROVAL",
                f"{grant.tool} on {grant.resource} exceeds the approved limit.",
            )

    grants = tuple(
        CompiledGrant(
            tool=grant.tool,
            resource=grant.resource,
            resource_type=tools[grant.tool].resource_type,
        )
        for grant in sorted(
            contract.allowed,
            key=lambda item: (item.tool, item.resource),
        )
    )

    # The ID identifies policy content, not an activation or session.
    payload = {
        "task_id": approval.task_id,
        "task": approval.task,
        "allowed": [asdict(grant) for grant in grants],
    }
    canonical_json = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    policy_id = sha256(canonical_json.encode("utf-8")).hexdigest()

    return CompiledPolicy(
        policy_id=policy_id,
        task_id=approval.task_id,
        task=approval.task,
        allowed=grants,
    )