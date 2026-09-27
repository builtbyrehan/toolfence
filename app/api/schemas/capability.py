from pydantic import BaseModel, ConfigDict, Field


class CapabilityResponse(BaseModel):
    tool: str
    granted: bool
    resource: str | None = None


class CapabilitiesResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    total: int
    granted: int
    excluded: int

    privilege_reduction_percent: float = Field(
        serialization_alias="privilegeReductionPercent",
    )

    capabilities: list[CapabilityResponse]
