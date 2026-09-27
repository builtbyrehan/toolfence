from __future__ import annotations

from collections import defaultdict
from typing import Any

from fastapi import APIRouter, HTTPException

from app.api.schemas.benchmark import (
    BenchmarkGroupResult,
    BenchmarkResponse,
)
from app.api.services.benchmark_reader import read_benchmark_report
from app.api.services.dashboard import normalize_benchmark_report


router = APIRouter()


def _build_groups(
    report: dict[str, Any],
) -> list[BenchmarkGroupResult]:
    raw_results = report.get(
        "results",
        []
    )

    if not isinstance(
        raw_results,
        list,
    ):
        raise ValueError(
            "Benchmark report field 'results' must be a list."
        )

    grouped: dict[
        str,
        dict[str, int],
    ] = defaultdict(
        lambda: {
            "total": 0,
            "correct": 0,
        }
    )

    for index, item in enumerate(
        raw_results
    ):
        if not isinstance(
            item,
            dict,
        ):
            raise ValueError(
                "Benchmark report contains an invalid "
                f"result at index {index}."
            )

        category = item.get(
            "category"
        )

        if not isinstance(
            category,
            str,
        ) or not category:
            raise ValueError(
                "Benchmark result is missing category "
                f"at index {index}."
            )

        correct = item.get(
            "correct"
        )

        if not isinstance(
            correct,
            bool,
        ):
            raise ValueError(
                "Benchmark result is missing boolean "
                f"'correct' at index {index}."
            )

        grouped[category][
            "total"
        ] += 1

        if correct:
            grouped[category][
                "correct"
            ] += 1

    return [
        BenchmarkGroupResult(
            label=category,
            total=values["total"],
            correct=values["correct"],
        )
        for category, values
        in sorted(
            grouped.items()
        )
    ]


@router.get(
    "/benchmark",
    response_model=BenchmarkResponse,
)
def get_benchmark() -> BenchmarkResponse:
    """
    Return ToolFence replay benchmark measurements.

    Timing values represent authorization policy-evaluation time,
    not end-to-end Bob or MCP latency.
    """

    try:
        normalized = (
            normalize_benchmark_report()
        )

        raw_report = (
            read_benchmark_report()
        )

        groups = _build_groups(
            raw_report
        )

        return BenchmarkResponse(
            total_cases=normalized[
                "total_cases"
            ],
            matched_cases=normalized[
                "matched_cases"
            ],
            ground_truth_match_percent=normalized[
                "ground_truth_match_percent"
            ],
            forbidden_action_blocking_percent=normalized[
                "forbidden_action_blocking_percent"
            ],
            false_denial_percent=normalized[
                "false_denial_percent"
            ],
            boundary_accuracy_percent=normalized[
                "boundary_accuracy_percent"
            ],
            privilege_reduction_percent=normalized[
                "privilege_reduction_percent"
            ],
            mean_policy_evaluation_ms=normalized[
                "mean_policy_evaluation_ms"
            ],
            max_policy_evaluation_ms=normalized[
                "max_policy_evaluation_ms"
            ],
            groups=groups,
        )

    except (
        OSError,
        TypeError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc
