from __future__ import annotations

from typing import Any, Literal

from mcp.server import MCPServer
from pydantic import (
    BaseModel,
    ConfigDict,
    TypeAdapter,
    ValidationError,
)

from app.application import ToolFenceApplication
from app.gateway.dispatcher import DispatchResult
from app.policy.controller import TaskControlError
from app.policy.schema import (
    CapabilityGrant,
    TaskID,
)


_TASK_ID_ADAPTER = TypeAdapter(TaskID)


class MCPResponseModel(BaseModel):
    """
    Shared strict response base for ToolFence MCP tools.
    """

    model_config = ConfigDict(
        extra="forbid",
    )


class CapabilityView(MCPResponseModel):
    tool: str
    service: str
    action: str
    resource_type: str
    description: str


class CapabilityInventoryResponse(MCPResponseModel):
    task_id: str
    capabilities: list[CapabilityView]


class PolicyProposalResponse(MCPResponseModel):
    accepted: bool

    task_id: str

    policy_id: str | None
    state: str | None

    grant_count: int

    error_code: str | None
    error: str | None


class PolicyStatusResponse(MCPResponseModel):
    task_id: str

    approval_registered: bool
    policy_registered: bool
    active: bool

    state: str
    policy_id: str | None


class DispatchEnvelope(MCPResponseModel):
    """
    MCP-safe representation of one ToolFence dispatch result.

    Authorization status and backend execution status remain separate.
    """

    decision: Literal["ALLOW", "DENY"]

    reason_code: str
    reason: str

    policy_id: str | None
    matched_scope: str | None

    execution_status: Literal[
        "NOT_EXECUTED",
        "SUCCEEDED",
        "FAILED",
    ]

    result: Any | None

    execution_error_code: str | None
    execution_error: str | None

    audit_event_id: int | None
    audit_error_code: str | None
    audit_error: str | None


def _validate_bound_task_id(
    task_id: str,
) -> str:
    try:
        return _TASK_ID_ADAPTER.validate_python(
            task_id,
            strict=True,
        )

    except ValidationError as exc:
        raise ValueError(
            "Invalid MCP bound task_id."
        ) from exc


def _dispatch_response(
    result: DispatchResult,
) -> DispatchEnvelope:
    return DispatchEnvelope(
        decision=result.decision,
        reason_code=result.reason_code,
        reason=result.reason,
        policy_id=result.policy_id,
        matched_scope=result.matched_scope,
        execution_status=result.execution_status,
        result=result.result,
        execution_error_code=(
            result.execution_error_code
        ),
        execution_error=result.execution_error,
        audit_event_id=result.audit_event_id,
        audit_error_code=result.audit_error_code,
        audit_error=result.audit_error,
    )


def create_mcp_server(
    application: ToolFenceApplication,
    *,
    bound_task_id: str,
) -> MCPServer:
    """
    Create an MCP server bound to exactly one trusted ToolFence task.

    Security properties:

    - The model cannot choose an arbitrary CompiledPolicy.
    - The model cannot choose another task_id for protected calls.
    - Bob may propose permissions but cannot provide its own approved limit.
    - Protected external operations always pass through the dispatcher.
    - ALLOW/DENY decisions therefore use the trusted active policy.
    - Backend execution remains separated from authorization.
    - Audit behavior remains inside the existing dispatcher.

    This factory does not create trusted approvals automatically.
    Trusted application/developer code must register an approval separately
    before Bob's proposal can activate a policy.
    """

    if not isinstance(
        application,
        ToolFenceApplication,
    ):
        raise TypeError(
            "application must be a "
            "ToolFenceApplication."
        )

    task_id = _validate_bound_task_id(
        bound_task_id
    )

    mcp = MCPServer(
        "ToolFence",
        instructions=(
            "ToolFence provides task-scoped developer tools. "
            f"This server is bound to task {task_id}. "
            "Inspect available capabilities, propose the minimum "
            "required policy, then use protected tools. "
            "A ToolFence DENY decision means the external action "
            "was not executed."
        ),
    )

    # ==============================================================
    # TOOLFENCE CONTROL PLANE
    # ==============================================================

    @mcp.tool(
        name="toolfence.list_capabilities",
        description=(
            "List the trusted external capability inventory available "
            "to the current ToolFence task."
        ),
    )
    def list_capabilities() -> CapabilityInventoryResponse:
        """
        List ToolFence's trusted external capability inventory.
        """

        capabilities = [
            CapabilityView(
                tool=capability.tool,
                service=capability.service,
                action=capability.action,
                resource_type=capability.resource_type,
                description=capability.description,
            )
            for capability
            in application.inventory.capabilities
        ]

        return CapabilityInventoryResponse(
            task_id=task_id,
            capabilities=capabilities,
        )

    @mcp.tool(
        name="toolfence.propose_policy",
        description=(
            "Submit the minimum Task Capability Contract proposed "
            "for this bound task. ToolFence validates it against a "
            "separately trusted developer-approved limit."
        ),
    )
    def propose_policy(
        task: str,
        allowed: list[CapabilityGrant],
    ) -> PolicyProposalResponse:
        """
        Submit Bob's capability proposal for this task.

        The task ID is NOT accepted from the model. It comes from the
        trusted MCP server binding.

        The approved permission limit is also NOT accepted from the model.
        TaskPolicyController retrieves it from TrustedApprovalStore.
        """

        proposal = {
            "task_id": task_id,
            "task": task,
            "allowed": [
                grant.model_dump()
                for grant in allowed
            ],
        }

        try:
            activation = (
                application.controller
                .submit_proposal(
                    proposal
                )
            )

        except TaskControlError as exc:
            return PolicyProposalResponse(
                accepted=False,
                task_id=task_id,
                policy_id=None,
                state=None,
                grant_count=0,
                error_code=exc.code,
                error=exc.message,
            )

        return PolicyProposalResponse(
            accepted=True,
            task_id=task_id,
            policy_id=(
                activation.policy.policy_id
            ),
            state=(
                activation.lifecycle.state
            ),
            grant_count=len(
                activation.policy.allowed
            ),
            error_code=None,
            error=None,
        )

    @mcp.tool(
        name="toolfence.policy_status",
        description=(
            "Inspect whether this bound task has a trusted approval "
            "and an active ToolFence policy."
        ),
    )
    def policy_status() -> PolicyStatusResponse:
        """
        Return trusted lifecycle status for the MCP-bound task.
        """

        approval_registered = (
            application.approvals.get(
                task_id
            )
            is not None
        )

        try:
            lifecycle = (
                application.policy_store.status(
                    task_id
                )
            )

        except KeyError:
            return PolicyStatusResponse(
                task_id=task_id,
                approval_registered=(
                    approval_registered
                ),
                policy_registered=False,
                active=False,
                state="UNREGISTERED",
                policy_id=None,
            )

        active_policy = (
            application.policy_store.get_active(
                task_id
            )
        )

        return PolicyStatusResponse(
            task_id=task_id,
            approval_registered=(
                approval_registered
            ),
            policy_registered=True,
            active=active_policy is not None,
            state=lifecycle.state,
            policy_id=lifecycle.policy_id,
        )

    # ==============================================================
    # TICKET TOOLS
    # ==============================================================

    @mcp.tool(
        name="ticket.get",
        description=(
            "Read a ticket through ToolFence authorization."
        ),
    )
    def ticket_get(
        ticket_id: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="ticket.get",
                arguments={
                    "ticket_id": ticket_id,
                },
            )
        )

    @mcp.tool(
        name="ticket.comment",
        description=(
            "Add a comment to a ticket through "
            "ToolFence authorization."
        ),
    )
    def ticket_comment(
        ticket_id: str,
        body: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="ticket.comment",
                arguments={
                    "ticket_id": ticket_id,
                    "body": body,
                },
            )
        )

    @mcp.tool(
        name="ticket.delete",
        description=(
            "Delete a ticket through ToolFence authorization."
        ),
    )
    def ticket_delete(
        ticket_id: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="ticket.delete",
                arguments={
                    "ticket_id": ticket_id,
                },
            )
        )

    # ==============================================================
    # REPOSITORY TOOLS
    # ==============================================================

    @mcp.tool(
        name="repo.read",
        description=(
            "Read a logical repository file through "
            "ToolFence authorization."
        ),
    )
    def repo_read(
        path: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="repo.read",
                arguments={
                    "path": path,
                },
            )
        )

    @mcp.tool(
        name="repo.write",
        description=(
            "Write a logical repository file through "
            "ToolFence authorization."
        ),
    )
    def repo_write(
        path: str,
        content: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="repo.write",
                arguments={
                    "path": path,
                    "content": content,
                },
            )
        )

    @mcp.tool(
        name="pull_request.create",
        description=(
            "Create a mock pull request through "
            "ToolFence authorization."
        ),
    )
    def pull_request_create(
        branch: str,
        title: str,
        body: str = "",
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="pull_request.create",
                arguments={
                    "branch": branch,
                    "title": title,
                    "body": body,
                },
            )
        )

    # ==============================================================
    # CI TOOLS
    # ==============================================================

    @mcp.tool(
        name="ci.run",
        description=(
            "Run the deterministic demo CI checks through "
            "ToolFence authorization."
        ),
    )
    def ci_run(
        branch: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="ci.run",
                arguments={
                    "branch": branch,
                },
            )
        )

    @mcp.tool(
        name="ci.status",
        description=(
            "Read the latest CI status through "
            "ToolFence authorization."
        ),
    )
    def ci_status(
        branch: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="ci.status",
                arguments={
                    "branch": branch,
                },
            )
        )

    # ==============================================================
    # RELEASE TOOLS
    # ==============================================================

    @mcp.tool(
        name="release.status",
        description=(
            "Read release environment status through "
            "ToolFence authorization."
        ),
    )
    def release_status(
        environment: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="release.status",
                arguments={
                    "environment": environment,
                },
            )
        )

    @mcp.tool(
        name="release.deploy",
        description=(
            "Deploy a version to a release environment through "
            "ToolFence authorization."
        ),
    )
    def release_deploy(
        environment: str,
        version: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="release.deploy",
                arguments={
                    "environment": environment,
                    "version": version,
                },
            )
        )

    # ==============================================================
    # SECRET TOOL
    # ==============================================================

    @mcp.tool(
        name="secret.read",
        description=(
            "Read a fake demo secret through "
            "ToolFence authorization."
        ),
    )
    def secret_read(
        secret_id: str,
    ) -> DispatchEnvelope:
        return _dispatch_response(
            application.dispatcher.dispatch(
                task_id=task_id,
                tool="secret.read",
                arguments={
                    "secret_id": secret_id,
                },
            )
        )

    return mcp