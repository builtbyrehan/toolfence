from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PolicyDecision = Literal[
    "ALLOW",
    "DENY",
]


class AuditEventResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    event_id: int = Field(
        serialization_alias="eventId",
    )

    task_id: str | None = Field(
        default=None,
        serialization_alias="taskId",
    )

    policy_id: str | None = Field(
        default=None,
        serialization_alias="policyId",
    )

    tool: str
    resource: str
    decision: PolicyDecision

    reason_code: str = Field(
        serialization_alias="reasonCode",
    )

    execution_status: str = Field(
        serialization_alias="executionStatus",
    )

    timestamp: str | None = None


class AuditResponse(BaseModel):
    total: int
    events: list[AuditEventResponse]
