from __future__ import annotations

import os
from pathlib import Path

from app.bootstrap import (
    ToolFenceBootstrap,
    bootstrap_golden_task,
)


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

CAPABILITY_PATH = (
    PROJECT_ROOT
    / "config"
    / "capabilities.json"
)

GOLDEN_TASK_PATH = (
    PROJECT_ROOT
    / "config"
    / "golden_task.json"
)

DEFAULT_AUDIT_PATH = (
    PROJECT_ROOT
    / "runtime"
    / "audit.jsonl"
)


def _audit_path() -> Path:
    """
    Resolve the audit-log path.

    Trusted security configuration is intentionally NOT configurable through
    environment variables here.

    Only the audit location may be overridden. This is useful for tests and
    alternate runtime storage without changing the trusted task approval.
    """

    configured = os.environ.get(
        "TOOLFENCE_AUDIT_PATH"
    )

    if configured is None:
        return DEFAULT_AUDIT_PATH

    if not configured.strip():
        return DEFAULT_AUDIT_PATH

    return Path(
        configured
    ).expanduser()


def create_runtime() -> ToolFenceBootstrap:
    """
    Build the trusted ToolFence MCP runtime.

    Capability inventory and golden-task approval are always loaded from
    this repository's trusted configuration directory.

    Bob cannot choose either configuration path.
    """

    return bootstrap_golden_task(
        capability_path=CAPABILITY_PATH,
        golden_task_path=GOLDEN_TASK_PATH,
        audit_path=_audit_path(),
    )


# MCP tooling and hosts may import this module and expect a server object.
# Keeping the object at module scope also allows commands such as:
#
#     mcp run app/mcp_stdio.py:mcp
#
# while direct execution continues to work with:
#
#     python -m app.mcp_stdio
#
runtime = create_runtime()

mcp = runtime.mcp_server


def main() -> None:
    """
    Run ToolFence using MCP STDIO transport.

    mcp.run() defaults to STDIO.

    Do not add print() calls here. stdout belongs to the MCP protocol
    transport while the server is running.
    """

    mcp.run()


if __name__ == "__main__":
    main()