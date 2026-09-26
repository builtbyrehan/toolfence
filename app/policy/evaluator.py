"""Deterministic authorization decisions for compiled task policies."""

from dataclasses import dataclass
from typing import Literal

from pydantic import Field, ValidationError

from app.policy.compiler import CompiledGrant, CompiledPolicy
from app.policy.matcher import (
    resource_matches,
    validate_resource,
    validate_resource_pattern,
)
from app.policy.schema import StrictModel, TaskID, ToolName


DecisionCode = Literal[
    "PERMITTED",
    "NO_ACTIVE_POLICY",
    "INVALID_POLICY",
    "INVALID_REQUEST",
    "TASK_MISMATCH",
    "TOOL_NOT_GRANTED",
    "INVALID_RESOURCE",
    "RESOURCE_OUT_OF_SCOPE",
    "POLICY_ERROR",
]


class ToolCallRequest(StrictModel):
    task_id: TaskID
    tool: ToolName
    resource: str = Field(min_length=1, max_length=512)


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    decision: Literal["ALLOW", "DENY"]
    reason_code: DecisionCode
    reason: str
    policy_id: str | None = None
    matched_scope: str | None = None

    @property
    def allowed(self) -> bool:
        return self.decision == "ALLOW"


def _deny(
    code: DecisionCode,
    reason: str,
    policy_id: str | None = None,
) -> AuthorizationDecision:
    return AuthorizationDecision(
        decision="DENY",
        reason_code=code,
        reason=reason,
        policy_id=policy_id,
    )


def evaluate_call(
    policy: CompiledPolicy | None,
    *,
    task_id: str,
    tool: str,
    resource: str,
) -> AuthorizationDecision:
    """Evaluate one call against the server-selected active policy.

    The server supplies the compiled policy and binds the task context.
    Clients must never be allowed to supply their own compiled policy.
    """
    policy_id: str | None = None

    try:
        try:
            request = ToolCallRequest(
                task_id=task_id,
                tool=tool,
                resource=resource,
            )
        except ValidationError:
            return _deny(
                "INVALID_REQUEST",
                "The call contains invalid task, tool, or resource fields.",
            )

        if policy is None:
            return _deny(
                "NO_ACTIVE_POLICY",
                "No active task policy is available.",
            )

        if not isinstance(policy, CompiledPolicy):
            return _deny(
                "INVALID_POLICY",
                "The active policy is not a compiled policy.",
            )

        if not isinstance(policy.policy_id, str) or not policy.policy_id:
            return _deny(
                "INVALID_POLICY",
                "The active policy has no valid identifier.",
            )

        policy_id = policy.policy_id

        if request.task_id != policy.task_id:
            return _deny(
                "TASK_MISMATCH",
                "The call belongs to a different task.",
                policy_id,
            )

        if not isinstance(policy.allowed, tuple):
            return _deny(
                "INVALID_POLICY",
                "The policy permission collection is invalid.",
                policy_id,
            )

        # Check all stored scopes before returning any ALLOW decision.
        try:
            for grant in policy.allowed:
                if not isinstance(grant, CompiledGrant):
                    raise ValueError("invalid compiled grant")
                validate_resource_pattern(grant.resource_type, grant.resource)
        except (TypeError, ValueError):
            return _deny(
                "INVALID_POLICY",
                "The policy contains an invalid permission.",
                policy_id,
            )

        grants = tuple(
            grant for grant in policy.allowed if grant.tool == request.tool
        )

        if not grants:
            return _deny(
                "TOOL_NOT_GRANTED",
                "The task policy does not grant this tool action.",
                policy_id,
            )

        resource_type = grants[0].resource_type

        if any(grant.resource_type != resource_type for grant in grants):
            return _deny(
                "INVALID_POLICY",
                "The policy assigns inconsistent resource types to a tool.",
                policy_id,
            )

        try:
            validate_resource(resource_type, request.resource)
        except ValueError as exc:
            return _deny(
                "INVALID_RESOURCE",
                str(exc),
                policy_id,
            )

        for grant in grants:
            if resource_matches(resource_type, grant.resource, request.resource):
                return AuthorizationDecision(
                    decision="ALLOW",
                    reason_code="PERMITTED",
                    reason="The tool and resource are permitted for this task.",
                    policy_id=policy_id,
                    matched_scope=grant.resource,
                )

        return _deny(
            "RESOURCE_OUT_OF_SCOPE",
            "The requested resource is outside the tool's granted scopes.",
            policy_id,
        )

    except Exception:
        # Unexpected authorization failures must never permit execution.
        return _deny(
            "POLICY_ERROR",
            "Authorization failed; the call was denied.",
            policy_id,
        )