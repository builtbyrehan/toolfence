from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from mcp.server import MCPServer
from pydantic import (
    BaseModel,
    ConfigDict,
    ValidationError,
    model_validator,
)

from app.application import (
    DEFAULT_AUDIT_PATH,
    DEFAULT_CAPABILITY_PATH,
    ToolFenceApplication,
    create_application,
)
from app.gateway.mcp_server import create_mcp_server
from app.policy.schema import (
    TaskCapabilityContract,
    TaskID,
)


DEFAULT_GOLDEN_TASK_PATH = Path(
    "config/golden_task.json"
)


class BootstrapConfigurationError(ValueError):
    """
    Raised when trusted ToolFence bootstrap configuration is invalid.
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


class GoldenTaskConfiguration(BaseModel):
    """
    Strict trusted configuration for the ToolFence golden task.

    The top-level task identity must exactly match the identity contained
    in approved_limit.
    """

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )

    schema_version: Literal["1.0"]

    task_id: TaskID

    task: str

    approved_limit: TaskCapabilityContract

    @model_validator(mode="after")
    def validate_consistency(
        self,
    ) -> "GoldenTaskConfiguration":
        if not self.task.strip():
            raise ValueError(
                "Golden task text cannot be blank."
            )

        if self.task != self.task.strip():
            raise ValueError(
                "Golden task text cannot contain "
                "surrounding whitespace."
            )

        if (
            self.approved_limit.task_id
            != self.task_id
        ):
            raise ValueError(
                "Golden task_id must match "
                "approved_limit.task_id."
            )

        if (
            self.approved_limit.task
            != self.task
        ):
            raise ValueError(
                "Golden task text must match "
                "approved_limit.task."
            )

        return self


@dataclass(frozen=True, slots=True)
class ToolFenceBootstrap:
    """
    Fully initialized ToolFence golden-task runtime.

    configuration:
        Trusted developer-controlled golden-task configuration.

    application:
        ToolFence application composition root.

    mcp_server:
        MCP server permanently bound to configuration.task_id.
    """

    configuration: GoldenTaskConfiguration

    application: ToolFenceApplication

    mcp_server: MCPServer


def load_golden_task_configuration(
    path: str | Path = DEFAULT_GOLDEN_TASK_PATH,
) -> GoldenTaskConfiguration:
    """
    Load and strictly validate trusted golden-task configuration.
    """

    config_path = Path(path)

    if not config_path.exists():
        raise BootstrapConfigurationError(
            "GOLDEN_TASK_FILE_NOT_FOUND",
            (
                "Golden-task configuration does not exist: "
                f"{config_path}"
            ),
        )

    if not config_path.is_file():
        raise BootstrapConfigurationError(
            "INVALID_GOLDEN_TASK_PATH",
            (
                "Golden-task configuration path is not "
                f"a file: {config_path}"
            ),
        )

    try:
        raw_text = config_path.read_text(
            encoding="utf-8"
        )

    except OSError as exc:
        raise BootstrapConfigurationError(
            "GOLDEN_TASK_READ_FAILED",
            "Unable to read golden-task configuration.",
        ) from exc

    try:
        raw_data = json.loads(
            raw_text
        )

    except json.JSONDecodeError as exc:
        raise BootstrapConfigurationError(
            "INVALID_GOLDEN_TASK_JSON",
            (
                "Golden-task configuration is not "
                "valid JSON."
            ),
        ) from exc

    try:
        return (
            GoldenTaskConfiguration
            .model_validate(
                raw_data,
                strict=True,
            )
        )

    except ValidationError as exc:
        raise BootstrapConfigurationError(
            "INVALID_GOLDEN_TASK_CONFIGURATION",
            (
                "Golden-task configuration failed "
                "schema validation."
            ),
        ) from exc


def bootstrap_golden_task(
    *,
    capability_path: str | Path = DEFAULT_CAPABILITY_PATH,
    golden_task_path: str | Path = DEFAULT_GOLDEN_TASK_PATH,
    audit_path: str | Path = DEFAULT_AUDIT_PATH,
) -> ToolFenceBootstrap:
    """
    Create the trusted ToolFence golden-task runtime.

    Steps:

    1. Load trusted golden-task configuration.
    2. Load trusted capability inventory.
    3. Create ToolFence services and enforcement components.
    4. Register the developer-approved permission limit.
    5. Create an MCP server bound to the trusted task_id.

    This function deliberately does NOT activate a policy.

    Bob must still submit a proposal through the ToolFence MCP control
    plane before protected actions can be allowed.
    """

    configuration = (
        load_golden_task_configuration(
            golden_task_path
        )
    )

    application = create_application(
        capability_path=capability_path,
        audit_path=audit_path,
    )

    application.approvals.register(
        configuration.approved_limit
    )

    mcp_server = create_mcp_server(
        application,
        bound_task_id=configuration.task_id,
    )

    return ToolFenceBootstrap(
        configuration=configuration,
        application=application,
        mcp_server=mcp_server,
    )