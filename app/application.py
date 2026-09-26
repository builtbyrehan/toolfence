from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from app.gateway.audit import AuditLog
from app.gateway.dispatcher import ProtectedToolDispatcher
from app.policy.controller import (
    TaskPolicyController,
    TrustedApprovalStore,
)
from app.policy.schema import CapabilityInventory
from app.policy.store import ActivePolicyStore

from mock_mcp.ci import CIService
from mock_mcp.release import ReleaseService
from mock_mcp.repository import RepositoryService
from mock_mcp.secrets import SecretService
from mock_mcp.tickets import TicketService


DEFAULT_CAPABILITY_PATH = Path(
    "config/capabilities.json"
)

DEFAULT_AUDIT_PATH = Path(
    "runtime/audit.jsonl"
)


class ApplicationConfigurationError(ValueError):
    """
    Raised when trusted ToolFence application configuration cannot be
    loaded or validated.

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


@dataclass(frozen=True, slots=True)
class ToolFenceApplication:
    """
    Fully wired in-process ToolFence application runtime.

    This object is the composition root for the MVP.

    Trust boundaries:

    - inventory:
        Trusted application capability configuration.

    - approvals:
        Trusted developer/application-approved task limits.

    - controller:
        Accepts Bob proposals, retrieves the separately stored approval,
        compiles the proposal, and activates the resulting policy.

    - policy_store:
        Stores trusted active policies used by protected runtime calls.

    - dispatcher:
        Performs validation, authorization, execution, and audit integration.

    No approval or policy is registered automatically.
    """

    inventory: CapabilityInventory

    approvals: TrustedApprovalStore
    policy_store: ActivePolicyStore
    controller: TaskPolicyController

    audit: AuditLog

    tickets: TicketService
    repository: RepositoryService
    ci: CIService
    release: ReleaseService
    secrets: SecretService

    dispatcher: ProtectedToolDispatcher


def create_application(
    *,
    capability_path: str | Path = DEFAULT_CAPABILITY_PATH,
    audit_path: str | Path = DEFAULT_AUDIT_PATH,
) -> ToolFenceApplication:
    """
    Build one correctly wired ToolFence runtime.

    Security properties:

    - Capability inventory comes from trusted application configuration.
    - Trusted approvals are stored separately from Bob proposals.
    - Bob-facing proposal processing cannot provide its own approval limit.
    - Compiled policies are activated through the trusted policy store.
    - CI and repository share the same repository state.
    - Protected execution uses the trusted active policy store.
    - Every validated protected request can be audited.
    - No task approval or active policy is created automatically.
    """

    inventory = load_capability_inventory(
        capability_path
    )

    approvals = TrustedApprovalStore()

    policy_store = ActivePolicyStore()

    controller = TaskPolicyController(
        inventory=inventory,
        approvals=approvals,
        policy_store=policy_store,
    )

    audit = AuditLog(
        audit_path
    )

    tickets = TicketService()

    repository = RepositoryService()

    # CI must inspect the exact same repository state modified through
    # repo.read and repo.write.
    ci = CIService(
        repository
    )

    release = ReleaseService()

    secrets = SecretService()

    dispatcher = ProtectedToolDispatcher(
        policy_store=policy_store,
        audit=audit,
        tickets=tickets,
        repository=repository,
        ci=ci,
        release=release,
        secrets=secrets,
    )

    return ToolFenceApplication(
        inventory=inventory,
        approvals=approvals,
        policy_store=policy_store,
        controller=controller,
        audit=audit,
        tickets=tickets,
        repository=repository,
        ci=ci,
        release=release,
        secrets=secrets,
        dispatcher=dispatcher,
    )


def load_capability_inventory(
    path: str | Path = DEFAULT_CAPABILITY_PATH,
) -> CapabilityInventory:
    """
    Load and strictly validate ToolFence's trusted capability inventory.

    The inventory belongs to trusted application configuration. It must not
    be supplied by Bob as trusted configuration.
    """

    inventory_path = Path(path)

    if not inventory_path.exists():
        raise ApplicationConfigurationError(
            "CAPABILITY_FILE_NOT_FOUND",
            (
                "Capability inventory does not exist: "
                f"{inventory_path}"
            ),
        )

    if not inventory_path.is_file():
        raise ApplicationConfigurationError(
            "INVALID_CAPABILITY_PATH",
            (
                "Capability inventory path is not a file: "
                f"{inventory_path}"
            ),
        )

    try:
        raw_text = inventory_path.read_text(
            encoding="utf-8"
        )

    except OSError as exc:
        raise ApplicationConfigurationError(
            "CAPABILITY_READ_FAILED",
            (
                "Unable to read the capability inventory."
            ),
        ) from exc

    try:
        raw_data = json.loads(
            raw_text
        )

    except json.JSONDecodeError as exc:
        raise ApplicationConfigurationError(
            "INVALID_CAPABILITY_JSON",
            (
                "Capability inventory is not valid JSON."
            ),
        ) from exc

    try:
        return CapabilityInventory.model_validate(
            raw_data
        )

    except ValidationError as exc:
        raise ApplicationConfigurationError(
            "INVALID_CAPABILITY_INVENTORY",
            (
                "Capability inventory failed schema validation."
            ),
        ) from exc