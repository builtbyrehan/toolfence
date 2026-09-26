from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
from time import perf_counter_ns
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    model_validator,
)

from app.application import load_capability_inventory
from app.bootstrap import load_golden_task_configuration
from app.policy.compiler import (
    CompiledPolicy,
    ContractValidationError,
    compile_contract,
)
from app.policy.evaluator import evaluate_call
from app.policy.schema import TaskID, ToolName


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

DEFAULT_GROUND_TRUTH_PATH = (
    PROJECT_ROOT
    / "benchmark"
    / "ground_truth.json"
)

DEFAULT_CAPABILITY_PATH = (
    PROJECT_ROOT
    / "config"
    / "capabilities.json"
)

DEFAULT_GOLDEN_TASK_PATH = (
    PROJECT_ROOT
    / "config"
    / "golden_task.json"
)

DEFAULT_REPORT_PATH = (
    PROJECT_ROOT
    / "runtime"
    / "benchmark_report.json"
)


class BenchmarkConfigurationError(ValueError):
    """
    Raised when benchmark configuration or ground truth is invalid.
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


class BenchmarkModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        frozen=True,
    )


class BenchmarkCase(BenchmarkModel):
    case_id: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[a-z0-9][a-z0-9-]*$",
    )

    category: Literal[
        "legitimate",
        "forbidden",
        "boundary",
    ]

    tool: ToolName

    resource: str = Field(
        min_length=1,
        max_length=512,
    )

    expected_decision: Literal[
        "ALLOW",
        "DENY",
    ]

    expected_reason_code: str = Field(
        min_length=1,
        max_length=128,
        pattern=r"^[A-Z0-9_]+$",
    )


class GroundTruthDocument(BenchmarkModel):
    schema_version: Literal["1.0"]

    task_id: TaskID

    description: str = Field(
        min_length=1,
        max_length=1000,
    )

    cases: list[BenchmarkCase] = Field(
        min_length=1,
        max_length=100,
    )

    @model_validator(mode="after")
    def validate_unique_cases(
        self,
    ) -> "GroundTruthDocument":
        case_ids = [
            case.case_id
            for case in self.cases
        ]

        if len(case_ids) != len(set(case_ids)):
            raise ValueError(
                "Benchmark case_id values must be unique."
            )

        return self


class BenchmarkCaseResult(BenchmarkModel):
    case_id: str

    category: Literal[
        "legitimate",
        "forbidden",
        "boundary",
    ]

    tool: str
    resource: str

    expected_decision: Literal[
        "ALLOW",
        "DENY",
    ]

    actual_decision: Literal[
        "ALLOW",
        "DENY",
    ]

    expected_reason_code: str
    actual_reason_code: str

    matched_scope: str | None

    correct: bool

    evaluation_ms: float


class BenchmarkMetrics(BenchmarkModel):
    total_cases: int
    correct_cases: int

    ground_truth_match_rate: float

    total_legitimate_cases: int
    false_denials: int
    false_denial_rate: float | None

    total_forbidden_cases: int
    correctly_blocked_forbidden_cases: int
    forbidden_action_blocking_rate: float | None

    total_boundary_cases: int
    correct_boundary_cases: int
    boundary_case_accuracy: float | None

    available_capabilities: int
    granted_capabilities: int
    privilege_reduction_ratio: float

    mean_authorization_evaluation_ms: float
    max_authorization_evaluation_ms: float


class BenchmarkReport(BenchmarkModel):
    schema_version: Literal["1.0"] = "1.0"

    task_id: str
    policy_id: str

    policy_grant_count: int

    results: list[BenchmarkCaseResult]

    metrics: BenchmarkMetrics


def load_ground_truth(
    path: str | Path = DEFAULT_GROUND_TRUTH_PATH,
) -> GroundTruthDocument:
    """
    Load and strictly validate benchmark ground truth.
    """

    ground_truth_path = Path(path)

    if not ground_truth_path.exists():
        raise BenchmarkConfigurationError(
            "GROUND_TRUTH_NOT_FOUND",
            (
                "Benchmark ground truth does not exist: "
                f"{ground_truth_path}"
            ),
        )

    if not ground_truth_path.is_file():
        raise BenchmarkConfigurationError(
            "INVALID_GROUND_TRUTH_PATH",
            (
                "Benchmark ground-truth path is not a file: "
                f"{ground_truth_path}"
            ),
        )

    try:
        raw_text = ground_truth_path.read_text(
            encoding="utf-8"
        )

    except OSError as exc:
        raise BenchmarkConfigurationError(
            "GROUND_TRUTH_READ_FAILED",
            "Unable to read benchmark ground truth.",
        ) from exc

    try:
        raw_data = json.loads(
            raw_text
        )

    except json.JSONDecodeError as exc:
        raise BenchmarkConfigurationError(
            "INVALID_GROUND_TRUTH_JSON",
            "Benchmark ground truth is not valid JSON.",
        ) from exc

    try:
        return GroundTruthDocument.model_validate(
            raw_data,
            strict=True,
        )

    except ValidationError as exc:
        raise BenchmarkConfigurationError(
            "INVALID_GROUND_TRUTH",
            (
                "Benchmark ground truth failed "
                "schema validation."
            ),
        ) from exc


def compile_benchmark_policy(
    *,
    capability_path: str | Path = DEFAULT_CAPABILITY_PATH,
    golden_task_path: str | Path = DEFAULT_GOLDEN_TASK_PATH,
) -> tuple[
    CompiledPolicy,
    int,
]:
    """
    Compile the trusted golden-task policy used by the replay benchmark.

    This is benchmark fixture setup, not the Bob-facing approval flow.

    The proposal used here is intentionally the trusted golden approval
    itself so the benchmark evaluates the same six-grant policy contents
    used by the golden demo.

    Bob-facing runtime activation still goes through TaskPolicyController
    and TrustedApprovalStore.
    """

    inventory = load_capability_inventory(
        capability_path
    )

    golden_task = (
        load_golden_task_configuration(
            golden_task_path
        )
    )

    approved_limit = (
        golden_task.approved_limit
    )

    try:
        policy = compile_contract(
            approved_limit,
            inventory=inventory,
            approved_limit=approved_limit,
        )

    except ContractValidationError as exc:
        raise BenchmarkConfigurationError(
            "BENCHMARK_POLICY_INVALID",
            exc.message,
        ) from exc

    available_capabilities = len(
        {
            capability.tool
            for capability
            in inventory.capabilities
        }
    )

    return (
        policy,
        available_capabilities,
    )


def run_benchmark(
    *,
    ground_truth_path: str | Path = DEFAULT_GROUND_TRUTH_PATH,
    capability_path: str | Path = DEFAULT_CAPABILITY_PATH,
    golden_task_path: str | Path = DEFAULT_GOLDEN_TASK_PATH,
) -> BenchmarkReport:
    """
    Replay every predefined authorization case against the compiled
    ToolFence golden-task policy.

    No benchmark decisions or metrics are hard-coded.
    """

    ground_truth = load_ground_truth(
        ground_truth_path
    )

    policy, available_capabilities = (
        compile_benchmark_policy(
            capability_path=capability_path,
            golden_task_path=golden_task_path,
        )
    )

    if ground_truth.task_id != policy.task_id:
        raise BenchmarkConfigurationError(
            "BENCHMARK_TASK_MISMATCH",
            (
                "Ground-truth task_id does not match "
                "the compiled benchmark policy."
            ),
        )

    results: list[BenchmarkCaseResult] = []

    for case in ground_truth.cases:
        started_ns = perf_counter_ns()

        decision = evaluate_call(
            policy,
            task_id=ground_truth.task_id,
            tool=case.tool,
            resource=case.resource,
        )

        elapsed_ns = (
            perf_counter_ns()
            - started_ns
        )

        elapsed_ms = (
            elapsed_ns
            / 1_000_000
        )

        correct = (
            decision.decision
            == case.expected_decision
            and decision.reason_code
            == case.expected_reason_code
        )

        results.append(
            BenchmarkCaseResult(
                case_id=case.case_id,
                category=case.category,
                tool=case.tool,
                resource=case.resource,
                expected_decision=(
                    case.expected_decision
                ),
                actual_decision=(
                    decision.decision
                ),
                expected_reason_code=(
                    case.expected_reason_code
                ),
                actual_reason_code=(
                    decision.reason_code
                ),
                matched_scope=(
                    decision.matched_scope
                ),
                correct=correct,
                evaluation_ms=elapsed_ms,
            )
        )

    metrics = _calculate_metrics(
        policy=policy,
        available_capabilities=(
            available_capabilities
        ),
        results=results,
    )

    return BenchmarkReport(
        task_id=ground_truth.task_id,
        policy_id=policy.policy_id,
        policy_grant_count=len(
            policy.allowed
        ),
        results=results,
        metrics=metrics,
    )


def _calculate_metrics(
    *,
    policy: CompiledPolicy,
    available_capabilities: int,
    results: list[BenchmarkCaseResult],
) -> BenchmarkMetrics:
    if not results:
        raise BenchmarkConfigurationError(
            "EMPTY_BENCHMARK",
            "Benchmark contains no cases.",
        )

    total_cases = len(results)

    correct_cases = sum(
        result.correct
        for result in results
    )

    ground_truth_match_rate = (
        correct_cases
        / total_cases
    )

    legitimate = [
        result
        for result in results
        if result.category == "legitimate"
    ]

    false_denials = sum(
        result.actual_decision == "DENY"
        for result in legitimate
    )

    false_denial_rate = (
        false_denials
        / len(legitimate)
        if legitimate
        else None
    )

    forbidden = [
        result
        for result in results
        if result.category == "forbidden"
    ]

    correctly_blocked_forbidden = sum(
        result.actual_decision == "DENY"
        and result.correct
        for result in forbidden
    )

    forbidden_action_blocking_rate = (
        correctly_blocked_forbidden
        / len(forbidden)
        if forbidden
        else None
    )

    boundary = [
        result
        for result in results
        if result.category == "boundary"
    ]

    correct_boundary_cases = sum(
        result.correct
        for result in boundary
    )

    boundary_case_accuracy = (
        correct_boundary_cases
        / len(boundary)
        if boundary
        else None
    )

    granted_capabilities = len(
        {
            grant.tool
            for grant in policy.allowed
        }
    )

    if available_capabilities < 1:
        raise BenchmarkConfigurationError(
            "INVALID_CAPABILITY_COUNT",
            (
                "Available capability count must "
                "be greater than zero."
            ),
        )

    privilege_reduction_ratio = (
        1
        - (
            granted_capabilities
            / available_capabilities
        )
    )

    evaluation_times = [
        result.evaluation_ms
        for result in results
    ]

    return BenchmarkMetrics(
        total_cases=total_cases,
        correct_cases=correct_cases,
        ground_truth_match_rate=(
            ground_truth_match_rate
        ),
        total_legitimate_cases=(
            len(legitimate)
        ),
        false_denials=false_denials,
        false_denial_rate=(
            false_denial_rate
        ),
        total_forbidden_cases=(
            len(forbidden)
        ),
        correctly_blocked_forbidden_cases=(
            correctly_blocked_forbidden
        ),
        forbidden_action_blocking_rate=(
            forbidden_action_blocking_rate
        ),
        total_boundary_cases=(
            len(boundary)
        ),
        correct_boundary_cases=(
            correct_boundary_cases
        ),
        boundary_case_accuracy=(
            boundary_case_accuracy
        ),
        available_capabilities=(
            available_capabilities
        ),
        granted_capabilities=(
            granted_capabilities
        ),
        privilege_reduction_ratio=(
            privilege_reduction_ratio
        ),
        mean_authorization_evaluation_ms=(
            mean(evaluation_times)
        ),
        max_authorization_evaluation_ms=(
            max(evaluation_times)
        ),
    )


def write_report(
    report: BenchmarkReport,
    path: str | Path = DEFAULT_REPORT_PATH,
) -> Path:
    """
    Persist the measured benchmark report as formatted JSON.
    """

    report_path = Path(path)

    try:
        report_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        report_path.write_text(
            report.model_dump_json(
                indent=2
            )
            + "\n",
            encoding="utf-8",
        )

    except OSError as exc:
        raise BenchmarkConfigurationError(
            "REPORT_WRITE_FAILED",
            (
                "Unable to write benchmark report: "
                f"{report_path}"
            ),
        ) from exc

    return report_path


def _percentage(
    value: float | None,
) -> str:
    if value is None:
        return "N/A"

    return f"{value * 100:.2f}%"


def print_summary(
    report: BenchmarkReport,
    report_path: Path,
) -> None:
    """
    Print a concise summary based entirely on the measured run.
    """

    metrics = report.metrics

    print(
        "ToolFence Replay Benchmark"
    )

    print(
        f"Task: {report.task_id}"
    )

    print(
        f"Policy: {report.policy_id}"
    )

    print(
        (
            "Cases matched: "
            f"{metrics.correct_cases}/"
            f"{metrics.total_cases}"
        )
    )

    print(
        (
            "Ground-truth match rate: "
            f"{_percentage(metrics.ground_truth_match_rate)}"
        )
    )

    print(
        (
            "Forbidden action blocking rate: "
            f"{_percentage(metrics.forbidden_action_blocking_rate)}"
        )
    )

    print(
        (
            "False denial rate: "
            f"{_percentage(metrics.false_denial_rate)}"
        )
    )

    print(
        (
            "Boundary case accuracy: "
            f"{_percentage(metrics.boundary_case_accuracy)}"
        )
    )

    print(
        (
            "Privilege reduction ratio: "
            f"{_percentage(metrics.privilege_reduction_ratio)}"
        )
    )

    print(
        (
            "Mean authorization evaluation: "
            f"{metrics.mean_authorization_evaluation_ms:.4f} ms"
        )
    )

    print(
        (
            "Max authorization evaluation: "
            f"{metrics.max_authorization_evaluation_ms:.4f} ms"
        )
    )

    print(
        f"Report: {report_path}"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run the ToolFence deterministic "
            "authorization replay benchmark."
        )
    )

    parser.add_argument(
        "--ground-truth",
        default=str(
            DEFAULT_GROUND_TRUTH_PATH
        ),
    )

    parser.add_argument(
        "--capabilities",
        default=str(
            DEFAULT_CAPABILITY_PATH
        ),
    )

    parser.add_argument(
        "--golden-task",
        default=str(
            DEFAULT_GOLDEN_TASK_PATH
        ),
    )

    parser.add_argument(
        "--output",
        default=str(
            DEFAULT_REPORT_PATH
        ),
    )

    args = parser.parse_args()

    report = run_benchmark(
        ground_truth_path=args.ground_truth,
        capability_path=args.capabilities,
        golden_task_path=args.golden_task,
    )

    report_path = write_report(
        report,
        args.output,
    )

    print_summary(
        report,
        report_path,
    )

    if (
        report.metrics.correct_cases
        != report.metrics.total_cases
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()