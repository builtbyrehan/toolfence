import json
import os
from pathlib import Path
from typing import Any


DEFAULT_BENCHMARK_PATH = "runtime/benchmark_report.json"


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def get_benchmark_path() -> Path:
    configured_path = os.getenv(
        "TOOLFENCE_BENCHMARK_PATH",
        DEFAULT_BENCHMARK_PATH,
    )

    path = Path(configured_path)

    if not path.is_absolute():
        path = get_project_root() / path

    return path


def read_benchmark_report() -> dict[str, Any]:
    path = get_benchmark_path()

    if not path.exists():
        raise FileNotFoundError(
            f"Benchmark report not found: {path}"
        )

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Benchmark report contains invalid JSON: {path}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "Benchmark report must contain a JSON object."
        )

    return data
