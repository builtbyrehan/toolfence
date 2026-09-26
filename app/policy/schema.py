"""Data formats for ToolFence's capability inventory and task contracts."""

from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
    model_validator,
)


def _array_to_tuple(value: object) -> object:
    """Accept JSON-style lists while storing collections as tuples."""
    if isinstance(value, list):
        return tuple(value)
    return value


class StrictModel(BaseModel):
    """Reject extra fields and incorrect types; prevent ordinary mutation."""

    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
        revalidate_instances="always",
    )


ToolName = Annotated[
    str,
    StringConstraints(
        min_length=3,
        max_length=128,
        pattern=r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$",
    ),
]

TaskID = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=64,
        pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]*$",
    ),
]

ServiceName = Literal["ticket", "repository", "ci", "release", "secrets"]

ResourceType = Literal[
    "ticket_id",
    "repo_path",
    "branch",
    "environment",
    "secret_id",
]


class CapabilityDefinition(StrictModel):
    """One available capability; listing it does not grant permission."""

    tool: ToolName
    service: ServiceName
    action: str = Field(
        min_length=1,
        max_length=64,
        pattern=r"^[a-z][a-z0-9_]*$",
    )
    resource_type: ResourceType
    description: str = Field(min_length=1, max_length=500, pattern=r"\S")

    @model_validator(mode="after")
    def action_matches_tool(self) -> Self:
        if self.action != self.tool.rsplit(".", 1)[1]:
            raise ValueError("action must match the final part of tool")
        return self


class CapabilityInventory(StrictModel):
    """The versioned catalog of available capabilities."""

    schema_version: Literal["1.0"]
    capabilities: Annotated[
        tuple[CapabilityDefinition, ...],
        BeforeValidator(_array_to_tuple),
        Field(min_length=1, max_length=128),
    ]

    @model_validator(mode="after")
    def unique_tools(self) -> Self:
        names = [capability.tool for capability in self.capabilities]
        if len(names) != len(set(names)):
            raise ValueError("inventory contains duplicate tool names")
        return self


class CapabilityGrant(StrictModel):
    """A proposed tool/resource permission, pending authorization checks."""

    tool: ToolName
    resource: str = Field(min_length=1, max_length=512)

    @field_validator("resource")
    @classmethod
    def resource_text_is_valid(cls, value: str) -> str:
        if value != value.strip():
            raise ValueError("resource must not have surrounding whitespace")
        if not value.isprintable():
            raise ValueError("resource must contain only printable characters")
        return value


class TaskCapabilityContract(StrictModel):
    """A task's proposed permissions; schema validity is not approval."""

    task_id: TaskID
    task: str = Field(min_length=1, max_length=4000, pattern=r"\S")
    allowed: Annotated[
        tuple[CapabilityGrant, ...],
        BeforeValidator(_array_to_tuple),
        Field(max_length=128),
    ]

    @model_validator(mode="after")
    def unique_grants(self) -> Self:
        pairs = [(grant.tool, grant.resource) for grant in self.allowed]
        if len(pairs) != len(set(pairs)):
            raise ValueError("contract contains duplicate tool/resource grants")
        return self