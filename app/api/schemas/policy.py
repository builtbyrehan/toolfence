from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


PolicyLifecycleStatus = Literal[
    "ACTIVE",
    "COMPLETED",
    "REVOKED",
    "EXPIRED",
]


class CapabilityGrantResponse(BaseModel):
    tool: str
    resource: str


class PolicyResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    task_id: str = Field(
        serialization_alias="taskId",
    )
    policy_id: str = Field(
        serialization_alias="policyId",
    )
    status: PolicyLifecycleStatus
    grants: list[CapabilityGrantResponse]
    granted_count: int = Field(
        serialization_alias="grantedCount",
    )
