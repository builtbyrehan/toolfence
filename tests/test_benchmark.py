from __future__ import annotations

import json
from pathlib import Path

import pytest

from benchmark.run_benchmark import (
    BenchmarkConfigurationError,
    load_ground_truth,
    run_benchmark,
    write_report,
)


def test_ground_truth_contains_expected_16_cases() -> None:
    ground_truth = load_ground_truth()

    assert ground_truth.schema_version == "1.0"
    assert ground_truth.task_id == "BUG-17-FIX"
    assert len(ground_truth.cases) == 16


def test_ground_truth_case_ids_are_unique() -> None:
    ground_truth = load_ground_truth()

    case_ids = [
        case.case_id
        for case in ground_truth.cases
    ]

    assert len(case_ids) == len(set(case_ids))


def test_benchmark_matches_all_ground_truth_cases() -> None:
    report = run_benchmark()

    assert report.metrics.total_cases == 16
    assert report.metrics.correct_cases == 16

    assert (
        report.metrics.ground_truth_match_rate
        == pytest.approx(1.0)
    )

    assert all(
        result.correct
        for result in report.results
    )


def test_benchmark_blocks_all_forbidden_actions() -> None:
    report = run_benchmark()

    metrics = report.metrics

    assert metrics.total_forbidden_cases == 4

    assert (
        metrics.correctly_blocked_forbidden_cases
        == 4
    )

    assert (
        metrics.forbidden_action_blocking_rate
        == pytest.approx(1.0)
    )


def test_benchmark_has_zero_false_denials() -> None:
    report = run_benchmark()

    metrics = report.metrics

    assert metrics.total_legitimate_cases == 7
    assert metrics.false_denials == 0

    assert (
        metrics.false_denial_rate
        == pytest.approx(0.0)
    )


def test_benchmark_handles_all_boundary_cases() -> None:
    report = run_benchmark()

    metrics = report.metrics

    assert metrics.total_boundary_cases == 5
    assert metrics.correct_boundary_cases == 5

    assert (
        metrics.boundary_case_accuracy
        == pytest.approx(1.0)
    )


def test_benchmark_measures_privilege_reduction() -> None:
    report = run_benchmark()

    metrics = report.metrics

    assert metrics.available_capabilities == 11
    assert metrics.granted_capabilities == 6

    expected_ratio = 1 - (6 / 11)

    assert (
        metrics.privilege_reduction_ratio
        == pytest.approx(expected_ratio)
    )


def test_benchmark_records_evaluation_timing() -> None:
    report = run_benchmark()

    metrics = report.metrics

    assert (
        metrics.mean_authorization_evaluation_ms
        >= 0
    )

    assert (
        metrics.max_authorization_evaluation_ms
        >= 0
    )

    assert (
        metrics.max_authorization_evaluation_ms
        >= metrics.mean_authorization_evaluation_ms
    )

    assert all(
        result.evaluation_ms >= 0
        for result in report.results
    )


def test_secret_read_is_denied_as_not_granted() -> None:
    report = run_benchmark()

    result = next(
        result
        for result in report.results
        if result.case_id
        == "deny-secret-read-production-key"
    )

    assert result.actual_decision == "DENY"

    assert (
        result.actual_reason_code
        == "TOOL_NOT_GRANTED"
    )

    assert result.matched_scope is None
    assert result.correct is True


def test_out_of_scope_repo_write_is_denied() -> None:
    report = run_benchmark()

    result = next(
        result
        for result in report.results
        if result.case_id
        == "deny-repo-write-tests"
    )

    assert result.actual_decision == "DENY"

    assert (
        result.actual_reason_code
        == "RESOURCE_OUT_OF_SCOPE"
    )

    assert result.matched_scope is None
    assert result.correct is True


def test_allowed_repo_write_matches_expected_scope() -> None:
    report = run_benchmark()

    result = next(
        result
        for result in report.results
        if result.case_id
        == "allow-repo-write-source"
    )

    assert result.actual_decision == "ALLOW"

    assert (
        result.actual_reason_code
        == "PERMITTED"
    )

    assert result.matched_scope == "project/src/*"
    assert result.correct is True


def test_report_can_be_written_and_reloaded(
    tmp_path: Path,
) -> None:
    report = run_benchmark()

    report_path = (
        tmp_path
        / "benchmark_report.json"
    )

    written_path = write_report(
        report,
        report_path,
    )

    assert written_path == report_path
    assert written_path.exists()

    raw = json.loads(
        written_path.read_text(
            encoding="utf-8"
        )
    )

    assert raw["schema_version"] == "1.0"
    assert raw["task_id"] == "BUG-17-FIX"

    assert (
        raw["metrics"]["total_cases"]
        == 16
    )

    assert (
        raw["metrics"]["correct_cases"]
        == 16
    )


def test_invalid_ground_truth_fails_closed(
    tmp_path: Path,
) -> None:
    invalid_path = (
        tmp_path
        / "invalid_ground_truth.json"
    )

    invalid_path.write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "task_id": "BUG-17-FIX",
                "description": "Invalid benchmark.",
                "cases": [],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        BenchmarkConfigurationError
    ) as exc_info:
        load_ground_truth(
            invalid_path
        )

    assert (
        exc_info.value.code
        == "INVALID_GROUND_TRUTH"
    )