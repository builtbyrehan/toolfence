from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.gateway.audit import AuditLog, AuditLogError
from app.policy.evaluator import evaluate_call
from app.policy.matcher import validate_resource
from app.policy.store import ActivePolicyStore, PolicyStoreError

from mock_mcp.ci import CIService
from mock_mcp.release import ReleaseService
from mock_mcp.repository import RepositoryService
from mock_mcp.secrets import SecretService
from mock_mcp.tickets import TicketService


Decision = Literal["ALLOW", "DENY"]

ExecutionStatus = Literal[
    "NOT_EXECUTED",
    "SUCCEEDED",
    "FAILED",
]


class ToolArguments(BaseModel):
    """
    Strict base model for protected tool arguments.

    Unknown arguments are rejected so a caller cannot smuggle additional
    execution parameters past authorization.
    """

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )


class TicketGetArguments(ToolArguments):
    ticket_id: str = Field(min_length=1, max_length=512)


class TicketCommentArguments(ToolArguments):
    ticket_id: str = Field(min_length=1, max_length=512)
    body: str = Field(min_length=1, max_length=4000)


class TicketDeleteArguments(ToolArguments):
    ticket_id: str = Field(min_length=1, max_length=512)


class RepoReadArguments(ToolArguments):
    path: str = Field(min_length=1, max_length=512)


class RepoWriteArguments(ToolArguments):
    path: str = Field(min_length=1, max_length=512)
    content: str = Field(max_length=200_000)


class PullRequestCreateArguments(ToolArguments):
    branch: str = Field(min_length=1, max_length=512)
    title: str = Field(min_length=1, max_length=200)
    body: str = Field(default="", max_length=4000)


class CIRunArguments(ToolArguments):
    branch: str = Field(min_length=1, max_length=512)


class CIStatusArguments(ToolArguments):
    branch: str = Field(min_length=1, max_length=512)


class ReleaseStatusArguments(ToolArguments):
    environment: str = Field(min_length=1, max_length=512)


class ReleaseDeployArguments(ToolArguments):
    environment: str = Field(min_length=1, max_length=512)
    version: str = Field(min_length=1, max_length=128)


class SecretReadArguments(ToolArguments):
    secret_id: str = Field(min_length=1, max_length=512)


@dataclass(frozen=True, slots=True)
class ValidatedToolCall:
    """
    Immutable validated representation of one protected tool request.
    """

    tool: str
    resource: str
    arguments: ToolArguments


@dataclass(frozen=True, slots=True)
class DispatchResult:
    """
    Final protected-dispatch result.

    Authorization and backend execution are represented separately.

    audit_event_id is present when the final event was successfully
    persisted.

    audit_error_code/audit_error make audit persistence failures visible
    without lying about whether the backend operation itself executed.
    """

    decision: Decision
    reason_code: str
    reason: str

    policy_id: str | None
    matched_scope: str | None

    execution_status: ExecutionStatus

    result: object | None

    execution_error_code: str | None
    execution_error: str | None

    audit_event_id: int | None = None
    audit_error_code: str | None = None
    audit_error: str | None = None

    @property
    def allowed(self) -> bool:
        return self.decision == "ALLOW"

    @property
    def succeeded(self) -> bool:
        return self.execution_status == "SUCCEEDED"

    @property
    def audited(self) -> bool:
        return self.audit_event_id is not None


class ProtectedToolDispatcher:
    """
    ToolFence protected execution layer.

    Responsibilities:

    1. Validate protected tool arguments.
    2. Derive the resource from the same validated arguments that will later
       be used for execution.
    3. Retrieve the trusted active policy using task_id.
    4. Evaluate the call deterministically.
    5. Execute the backend only after ALLOW.
    6. Persist authorization and execution metadata to the audit log.

    The caller never supplies a CompiledPolicy directly.
    """

    def __init__(
        self,
        *,
        policy_store: ActivePolicyStore,
        audit: AuditLog,
        tickets: TicketService,
        repository: RepositoryService,
        ci: CIService,
        release: ReleaseService,
        secrets: SecretService,
    ) -> None:
        if not isinstance(policy_store, ActivePolicyStore):
            raise TypeError(
                "policy_store must be an ActivePolicyStore."
            )

        if not isinstance(audit, AuditLog):
            raise TypeError(
                "audit must be an AuditLog."
            )

        if not isinstance(tickets, TicketService):
            raise TypeError(
                "tickets must be a TicketService."
            )

        if not isinstance(repository, RepositoryService):
            raise TypeError(
                "repository must be a RepositoryService."
            )

        if not isinstance(ci, CIService):
            raise TypeError(
                "ci must be a CIService."
            )

        if not isinstance(release, ReleaseService):
            raise TypeError(
                "release must be a ReleaseService."
            )

        if not isinstance(secrets, SecretService):
            raise TypeError(
                "secrets must be a SecretService."
            )

        self._policy_store = policy_store
        self._audit = audit

        self._tickets = tickets
        self._repository = repository
        self._ci = ci
        self._release = release
        self._secrets = secrets

    def dispatch(
        self,
        *,
        task_id: str,
        tool: str,
        arguments: object,
    ) -> DispatchResult:
        """
        Authorize and, when permitted, execute one protected tool call.

        Requests that cannot be safely validated fail closed.

        Audit events are created once a request has a validated tool and
        resource identity.
        """

        # --------------------------------------------------------------
        # VALIDATE TOOL + ARGUMENTS + RESOURCE
        # --------------------------------------------------------------

        try:
            validated_call = self._validate_tool_call(
                tool=tool,
                arguments=arguments,
            )

        except KeyError:
            return DispatchResult(
                decision="DENY",
                reason_code="UNKNOWN_TOOL",
                reason=(
                    "The requested tool is not protected by "
                    "this gateway."
                ),
                policy_id=None,
                matched_scope=None,
                execution_status="NOT_EXECUTED",
                result=None,
                execution_error_code=None,
                execution_error=None,
            )

        except (
            ValidationError,
            ValueError,
            TypeError,
        ):
            return DispatchResult(
                decision="DENY",
                reason_code="INVALID_ARGUMENTS",
                reason=(
                    "Tool arguments are invalid for the "
                    "requested tool."
                ),
                policy_id=None,
                matched_scope=None,
                execution_status="NOT_EXECUTED",
                result=None,
                execution_error_code=None,
                execution_error=None,
            )

        # --------------------------------------------------------------
        # LOOK UP TRUSTED ACTIVE POLICY
        # --------------------------------------------------------------

        try:
            policy = self._policy_store.get_active(
                task_id
            )

        except PolicyStoreError:
            result = DispatchResult(
                decision="DENY",
                reason_code="POLICY_STORE_ERROR",
                reason=(
                    "The trusted policy store could not "
                    "determine the active policy."
                ),
                policy_id=None,
                matched_scope=None,
                execution_status="NOT_EXECUTED",
                result=None,
                execution_error_code=None,
                execution_error=None,
            )

            return self._attach_audit(
                task_id=task_id,
                call=validated_call,
                result=result,
            )

        except ValueError:
            return DispatchResult(
                decision="DENY",
                reason_code="INVALID_TASK_ID",
                reason="The task identifier is invalid.",
                policy_id=None,
                matched_scope=None,
                execution_status="NOT_EXECUTED",
                result=None,
                execution_error_code=None,
                execution_error=None,
            )

        # --------------------------------------------------------------
        # AUTHORIZE
        # --------------------------------------------------------------

        decision = evaluate_call(
            policy,
            task_id=task_id,
            tool=validated_call.tool,
            resource=validated_call.resource,
        )

        if not decision.allowed:
            result = DispatchResult(
                decision=decision.decision,
                reason_code=decision.reason_code,
                reason=decision.reason,
                policy_id=decision.policy_id,
                matched_scope=decision.matched_scope,
                execution_status="NOT_EXECUTED",
                result=None,
                execution_error_code=None,
                execution_error=None,
            )

            return self._attach_audit(
                task_id=task_id,
                call=validated_call,
                result=result,
            )

        # --------------------------------------------------------------
        # EXECUTE ONLY AFTER ALLOW
        # --------------------------------------------------------------

        try:
            backend_result = self._execute(
                validated_call
            )

        except (
            KeyError,
            ValueError,
            TypeError,
        ) as exc:
            result = DispatchResult(
                decision=decision.decision,
                reason_code=decision.reason_code,
                reason=decision.reason,
                policy_id=decision.policy_id,
                matched_scope=decision.matched_scope,
                execution_status="FAILED",
                result=None,
                execution_error_code="BACKEND_REJECTED",
                execution_error=str(exc),
            )

            return self._attach_audit(
                task_id=task_id,
                call=validated_call,
                result=result,
            )

        except Exception:
            result = DispatchResult(
                decision=decision.decision,
                reason_code=decision.reason_code,
                reason=decision.reason,
                policy_id=decision.policy_id,
                matched_scope=decision.matched_scope,
                execution_status="FAILED",
                result=None,
                execution_error_code="BACKEND_ERROR",
                execution_error=(
                    "The protected backend operation failed."
                ),
            )

            return self._attach_audit(
                task_id=task_id,
                call=validated_call,
                result=result,
            )

        result = DispatchResult(
            decision=decision.decision,
            reason_code=decision.reason_code,
            reason=decision.reason,
            policy_id=decision.policy_id,
            matched_scope=decision.matched_scope,
            execution_status="SUCCEEDED",
            result=deepcopy(backend_result),
            execution_error_code=None,
            execution_error=None,
        )

        return self._attach_audit(
            task_id=task_id,
            call=validated_call,
            result=result,
        )

    def _attach_audit(
        self,
        *,
        task_id: str,
        call: ValidatedToolCall,
        result: DispatchResult,
    ) -> DispatchResult:
        """
        Persist the final dispatch metadata.

        The backend result payload itself is deliberately not passed to
        AuditLog.
        """

        try:
            event = self._audit.record(
                task_id=task_id,
                tool=call.tool,
                resource=call.resource,
                decision=result.decision,
                reason_code=result.reason_code,
                reason=result.reason,
                policy_id=result.policy_id,
                matched_scope=result.matched_scope,
                execution_status=result.execution_status,
                execution_error_code=(
                    result.execution_error_code
                ),
                execution_error=result.execution_error,
            )

        except AuditLogError as exc:
            return replace(
                result,
                audit_error_code=exc.code,
                audit_error=exc.message,
            )

        except Exception:
            return replace(
                result,
                audit_error_code="AUDIT_ERROR",
                audit_error=(
                    "Audit persistence failed unexpectedly."
                ),
            )

        return replace(
            result,
            audit_event_id=event.event_id,
        )

    def _validate_tool_call(
        self,
        *,
        tool: str,
        arguments: object,
    ) -> ValidatedToolCall:
        if not isinstance(tool, str):
            raise TypeError(
                "Tool name must be a string."
            )

        if not isinstance(arguments, dict):
            raise TypeError(
                "Tool arguments must be a dictionary."
            )

        if tool == "ticket.get":
            parsed = TicketGetArguments.model_validate(
                arguments
            )

            validate_resource(
                "ticket_id",
                parsed.ticket_id,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.ticket_id,
                arguments=parsed,
            )

        if tool == "ticket.comment":
            parsed = TicketCommentArguments.model_validate(
                arguments
            )

            validate_resource(
                "ticket_id",
                parsed.ticket_id,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.ticket_id,
                arguments=parsed,
            )

        if tool == "ticket.delete":
            parsed = TicketDeleteArguments.model_validate(
                arguments
            )

            validate_resource(
                "ticket_id",
                parsed.ticket_id,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.ticket_id,
                arguments=parsed,
            )

        if tool == "repo.read":
            parsed = RepoReadArguments.model_validate(
                arguments
            )

            validate_resource(
                "repo_path",
                parsed.path,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.path,
                arguments=parsed,
            )

        if tool == "repo.write":
            parsed = RepoWriteArguments.model_validate(
                arguments
            )

            validate_resource(
                "repo_path",
                parsed.path,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.path,
                arguments=parsed,
            )

        if tool == "pull_request.create":
            parsed = (
                PullRequestCreateArguments
                .model_validate(arguments)
            )

            validate_resource(
                "branch",
                parsed.branch,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.branch,
                arguments=parsed,
            )

        if tool == "ci.run":
            parsed = CIRunArguments.model_validate(
                arguments
            )

            validate_resource(
                "branch",
                parsed.branch,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.branch,
                arguments=parsed,
            )

        if tool == "ci.status":
            parsed = CIStatusArguments.model_validate(
                arguments
            )

            validate_resource(
                "branch",
                parsed.branch,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.branch,
                arguments=parsed,
            )

        if tool == "release.status":
            parsed = (
                ReleaseStatusArguments
                .model_validate(arguments)
            )

            validate_resource(
                "environment",
                parsed.environment,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.environment,
                arguments=parsed,
            )

        if tool == "release.deploy":
            parsed = (
                ReleaseDeployArguments
                .model_validate(arguments)
            )

            validate_resource(
                "environment",
                parsed.environment,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.environment,
                arguments=parsed,
            )

        if tool == "secret.read":
            parsed = SecretReadArguments.model_validate(
                arguments
            )

            validate_resource(
                "secret_id",
                parsed.secret_id,
            )

            return ValidatedToolCall(
                tool=tool,
                resource=parsed.secret_id,
                arguments=parsed,
            )

        raise KeyError(
            f"Unknown protected tool: {tool}"
        )

    def _execute(
        self,
        call: ValidatedToolCall,
    ) -> object:
        """
        Execute using the exact validated argument object from which the
        authorization resource was derived.
        """

        arguments = call.arguments

        if call.tool == "ticket.get":
            assert isinstance(
                arguments,
                TicketGetArguments,
            )

            return self._tickets.get(
                arguments.ticket_id
            )

        if call.tool == "ticket.comment":
            assert isinstance(
                arguments,
                TicketCommentArguments,
            )

            return self._tickets.comment(
                arguments.ticket_id,
                arguments.body,
            )

        if call.tool == "ticket.delete":
            assert isinstance(
                arguments,
                TicketDeleteArguments,
            )

            return self._tickets.delete(
                arguments.ticket_id
            )

        if call.tool == "repo.read":
            assert isinstance(
                arguments,
                RepoReadArguments,
            )

            return self._repository.read(
                arguments.path
            )

        if call.tool == "repo.write":
            assert isinstance(
                arguments,
                RepoWriteArguments,
            )

            return self._repository.write(
                arguments.path,
                arguments.content,
            )

        if call.tool == "pull_request.create":
            assert isinstance(
                arguments,
                PullRequestCreateArguments,
            )

            return self._repository.create_pull_request(
                arguments.branch,
                arguments.title,
                arguments.body,
            )

        if call.tool == "ci.run":
            assert isinstance(
                arguments,
                CIRunArguments,
            )

            return self._ci.run(
                arguments.branch
            )

        if call.tool == "ci.status":
            assert isinstance(
                arguments,
                CIStatusArguments,
            )

            return self._ci.status(
                arguments.branch
            )

        if call.tool == "release.status":
            assert isinstance(
                arguments,
                ReleaseStatusArguments,
            )

            return self._release.status(
                arguments.environment
            )

        if call.tool == "release.deploy":
            assert isinstance(
                arguments,
                ReleaseDeployArguments,
            )

            return self._release.deploy(
                arguments.environment,
                arguments.version,
            )

        if call.tool == "secret.read":
            assert isinstance(
                arguments,
                SecretReadArguments,
            )

            return self._secrets.read(
                arguments.secret_id
            )

        raise RuntimeError(
            "Validated tool has no execution handler."
        )