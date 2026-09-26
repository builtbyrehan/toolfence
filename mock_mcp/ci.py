from __future__ import annotations

import ast
from copy import deepcopy
from threading import RLock
from typing import Literal, TypedDict

from app.policy.matcher import validate_resource
from mock_mcp.repository import (
    DEMO_REPOSITORY,
    TASK_BRANCH,
    RepositoryService,
)


SOURCE_PATH = "project/src/cart.py"
TEST_PATH = "project/tests/test_cart.py"


CIState = Literal["NOT_RUN", "PASSED", "FAILED", "ERROR"]


class CICheckResult(TypedDict):
    name: str
    prices: list[int]
    expected: int
    actual: int | None
    passed: bool


class CIRunRecord(TypedDict):
    run_id: int | None
    repository: str
    branch: str
    status: CIState
    checks: list[CICheckResult]
    error: str | None


class UnsupportedImplementationError(ValueError):
    """
    Raised when the demo CI encounters valid Python that falls outside the
    intentionally small expression subset supported by this mock service.
    """


class CIService:
    """
    Deterministic in-memory CI backend for the ToolFence golden demo.

    CI reads the current state from the same RepositoryService instance used
    by repo.read and repo.write.

    It deliberately does not execute arbitrary repository Python code.
    Instead, it parses the source with ast and safely evaluates the supported
    calculate_total expression against predefined acceptance cases.
    """

    def __init__(self, repository: RepositoryService) -> None:
        if not isinstance(repository, RepositoryService):
            raise TypeError(
                "CIService requires a RepositoryService instance."
            )

        self._repository = repository
        self._lock = RLock()
        self._runs: list[CIRunRecord] = []

    def run(self, branch: str) -> CIRunRecord:
        """
        Run the deterministic demo CI checks against the current repository.

        Returns:
            A safe copy of the recorded CI run.

        Raises:
            ValueError:
                If the branch resource identifier is invalid.

            KeyError:
                If the requested branch is not the demo task branch.
        """
        self._validate_branch(branch)

        snapshot = self._repository.snapshot()

        if snapshot["repository"] != DEMO_REPOSITORY:
            return self._record_error(
                branch,
                "Repository snapshot does not belong to the demo repository.",
            )

        if snapshot["branch"] != branch:
            return self._record_error(
                branch,
                "Repository snapshot branch does not match the CI branch.",
            )

        files = snapshot["files"]

        source = files.get(SOURCE_PATH)
        if source is None:
            return self._record_error(
                branch,
                f"Required source file is missing: {SOURCE_PATH}",
            )

        test_source = files.get(TEST_PATH)
        if test_source is None:
            return self._record_error(
                branch,
                f"Required test file is missing: {TEST_PATH}",
            )

        # Validate that the seeded test file still contains syntactically
        # valid Python. The mock CI does not execute this file.
        try:
            ast.parse(test_source, filename=TEST_PATH)
        except SyntaxError as exc:
            return self._record_failed_syntax(
                branch,
                f"Test file syntax error: {self._format_syntax_error(exc)}",
            )

        try:
            module = ast.parse(source, filename=SOURCE_PATH)
        except SyntaxError as exc:
            return self._record_failed_syntax(
                branch,
                f"Source syntax error: {self._format_syntax_error(exc)}",
            )

        try:
            function = self._find_calculate_total(module)
            checks = self._execute_checks(function)
        except UnsupportedImplementationError as exc:
            return self._record_error(branch, str(exc))

        status: CIState = (
            "PASSED"
            if all(check["passed"] for check in checks)
            else "FAILED"
        )

        with self._lock:
            record: CIRunRecord = {
                "run_id": len(self._runs) + 1,
                "repository": DEMO_REPOSITORY,
                "branch": branch,
                "status": status,
                "checks": deepcopy(checks),
                "error": None,
            }

            self._runs.append(deepcopy(record))
            return deepcopy(record)

    def status(self, branch: str) -> CIRunRecord:
        """
        Return the most recent CI result for the branch.

        If CI has never run, returns NOT_RUN rather than inventing a result.
        """
        self._validate_branch(branch)

        with self._lock:
            for record in reversed(self._runs):
                if record["branch"] == branch:
                    return deepcopy(record)

        return {
            "run_id": None,
            "repository": DEMO_REPOSITORY,
            "branch": branch,
            "status": "NOT_RUN",
            "checks": [],
            "error": None,
        }

    def _validate_branch(self, branch: str) -> None:
        validate_resource("branch", branch)

        if branch != TASK_BRANCH:
            raise KeyError(f"Unknown CI branch: {branch}")

    @staticmethod
    def _find_calculate_total(
        module: ast.Module,
    ) -> ast.FunctionDef:
        candidates = [
            node
            for node in module.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "calculate_total"
        ]

        if len(candidates) != 1:
            raise UnsupportedImplementationError(
                "CI requires exactly one top-level "
                "calculate_total function."
            )

        function = candidates[0]

        if function.decorator_list:
            raise UnsupportedImplementationError(
                "Decorated calculate_total functions are not supported "
                "by the demo CI."
            )

        args = function.args

        if (
            len(args.posonlyargs) != 0
            or len(args.args) != 1
            or args.args[0].arg != "prices"
            or args.vararg is not None
            or len(args.kwonlyargs) != 0
            or args.kwarg is not None
            or len(args.defaults) != 0
            or len(args.kw_defaults) != 0
        ):
            raise UnsupportedImplementationError(
                "calculate_total must have the signature "
                "calculate_total(prices)."
            )

        if len(function.body) != 1:
            raise UnsupportedImplementationError(
                "The demo CI currently supports calculate_total "
                "implementations containing one return statement."
            )

        statement = function.body[0]

        if not isinstance(statement, ast.Return):
            raise UnsupportedImplementationError(
                "The demo CI currently supports calculate_total "
                "implementations containing one return statement."
            )

        if statement.value is None:
            raise UnsupportedImplementationError(
                "calculate_total must return a value."
            )

        return function

    def _execute_checks(
        self,
        function: ast.FunctionDef,
    ) -> list[CICheckResult]:
        return_statement = function.body[0]

        if not isinstance(return_statement, ast.Return):
            raise UnsupportedImplementationError(
                "calculate_total does not contain a supported return."
            )

        expression = return_statement.value

        if expression is None:
            raise UnsupportedImplementationError(
                "calculate_total must return a value."
            )

        cases = (
            ("multiple_items", [10, 20, 30], 60),
            ("empty_cart", [], 0),
            ("single_item", [25], 25),
        )

        results: list[CICheckResult] = []

        for name, prices, expected in cases:
            actual_value = self._evaluate_expression(
                expression,
                list(prices),
            )

            if type(actual_value) is not int:
                raise UnsupportedImplementationError(
                    "calculate_total must produce an integer result "
                    "for the demo fixture."
                )

            results.append(
                {
                    "name": name,
                    "prices": list(prices),
                    "expected": expected,
                    "actual": actual_value,
                    "passed": actual_value == expected,
                }
            )

        return results

    def _evaluate_expression(
        self,
        node: ast.expr,
        prices: list[int],
    ) -> object:
        """
        Safely interpret the tiny expression language needed by the demo.

        Supported examples:

            sum(prices)
            sum(prices[1:])
            sum(prices[:])
            sum(prices[0:])
        """

        if isinstance(node, ast.Name):
            if node.id == "prices":
                return list(prices)

            raise UnsupportedImplementationError(
                f"Unsupported variable in calculate_total: {node.id}"
            )

        if isinstance(node, ast.Call):
            if not (
                isinstance(node.func, ast.Name)
                and node.func.id == "sum"
            ):
                raise UnsupportedImplementationError(
                    "The demo CI only supports the sum(...) function call."
                )

            if len(node.args) != 1 or node.keywords:
                raise UnsupportedImplementationError(
                    "sum(...) must contain exactly one positional argument."
                )

            value = self._evaluate_expression(node.args[0], prices)

            if not isinstance(value, list):
                raise UnsupportedImplementationError(
                    "sum(...) must operate on the prices list or a slice "
                    "of that list."
                )

            if not all(type(item) is int for item in value):
                raise UnsupportedImplementationError(
                    "The demo CI expects integer price values."
                )

            return sum(value)

        if isinstance(node, ast.Subscript):
            value = self._evaluate_expression(node.value, prices)

            if not isinstance(value, list):
                raise UnsupportedImplementationError(
                    "Only the prices list can be sliced."
                )

            if isinstance(node.slice, ast.Slice):
                start = self._slice_integer(node.slice.lower)
                stop = self._slice_integer(node.slice.upper)
                step = self._slice_integer(node.slice.step)

                if step == 0:
                    raise UnsupportedImplementationError(
                        "Slice step cannot be zero."
                    )

                return value[slice(start, stop, step)]

            index = self._slice_integer(node.slice)

            if index is None:
                raise UnsupportedImplementationError(
                    "Invalid list index."
                )

            try:
                return value[index]
            except IndexError:
                raise UnsupportedImplementationError(
                    "calculate_total attempted an out-of-range list index."
                ) from None

        raise UnsupportedImplementationError(
            "calculate_total uses Python syntax that the safe demo CI "
            "does not support."
        )

    @staticmethod
    def _slice_integer(node: ast.expr | None) -> int | None:
        if node is None:
            return None

        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value

        if (
            isinstance(node, ast.UnaryOp)
            and isinstance(node.op, ast.USub)
            and isinstance(node.operand, ast.Constant)
            and type(node.operand.value) is int
        ):
            return -node.operand.value

        raise UnsupportedImplementationError(
            "The demo CI only supports integer slice indexes."
        )

    def _record_error(
        self,
        branch: str,
        message: str,
    ) -> CIRunRecord:
        with self._lock:
            record: CIRunRecord = {
                "run_id": len(self._runs) + 1,
                "repository": DEMO_REPOSITORY,
                "branch": branch,
                "status": "ERROR",
                "checks": [],
                "error": message,
            }

            self._runs.append(deepcopy(record))
            return deepcopy(record)

    def _record_failed_syntax(
        self,
        branch: str,
        message: str,
    ) -> CIRunRecord:
        with self._lock:
            record: CIRunRecord = {
                "run_id": len(self._runs) + 1,
                "repository": DEMO_REPOSITORY,
                "branch": branch,
                "status": "FAILED",
                "checks": [],
                "error": message,
            }

            self._runs.append(deepcopy(record))
            return deepcopy(record)

    @staticmethod
    def _format_syntax_error(exc: SyntaxError) -> str:
        if exc.lineno is None:
            return exc.msg

        return f"line {exc.lineno}: {exc.msg}"