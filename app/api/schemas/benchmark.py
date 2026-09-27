from pydantic import BaseModel, ConfigDict, Field


class BenchmarkGroupResult(BaseModel):
    label: str
    total: int
    correct: int


class BenchmarkResponse(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )

    total_cases: int = Field(
        serialization_alias="totalCases",
    )

    matched_cases: int = Field(
        serialization_alias="matchedCases",
    )

    ground_truth_match_percent: float = Field(
        serialization_alias="groundTruthMatchPercent",
    )

    forbidden_action_blocking_percent: float = Field(
        serialization_alias="forbiddenActionBlockingPercent",
    )

    false_denial_percent: float = Field(
        serialization_alias="falseDenialPercent",
    )

    boundary_accuracy_percent: float = Field(
        serialization_alias="boundaryAccuracyPercent",
    )

    privilege_reduction_percent: float = Field(
        serialization_alias="privilegeReductionPercent",
    )

    mean_policy_evaluation_ms: float = Field(
        serialization_alias="meanPolicyEvaluationMs",
    )

    max_policy_evaluation_ms: float = Field(
        serialization_alias="maxPolicyEvaluationMs",
    )

    groups: list[BenchmarkGroupResult] | None = None
