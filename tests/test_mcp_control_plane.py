from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)


EXPECTED_TOOLS = {
    "toolfence.list_capabilities",
    "toolfence.task_context",
    "toolfence.propose_policy",
    "toolfence.policy_status",
    "ticket.get",
    "ticket.comment",
    "ticket.delete",
    "repo.read",
    "repo.write",
    "pull_request.create",
    "ci.run",
    "ci.status",
    "release.status",
    "release.deploy",
    "secret.read",
}


def _extract_structured_result(
    result: Any,
) -> dict[str, Any]:
    """
    Extract a JSON object from an MCP tool result.

    Supports either structured MCP output or JSON text content.
    """

    structured = getattr(
        result,
        "structuredContent",
        None,
    )

    if structured is None:
        structured = getattr(
            result,
            "structured_content",
            None,
        )

    if isinstance(
        structured,
        dict,
    ):
        return structured

    for item in result.content:
        text = getattr(
            item,
            "text",
            None,
        )

        if not text:
            continue

        try:
            parsed = json.loads(
                text
            )
        except json.JSONDecodeError:
            continue

        if isinstance(
            parsed,
            dict,
        ):
            return parsed

    raise AssertionError(
        "MCP result did not contain "
        "a structured JSON object."
    )


async def _inspect_control_plane() -> tuple[
    list[str],
    dict[str, Any],
    dict[str, Any],
]:
    """
    Start a real ToolFence STDIO MCP subprocess and inspect the
    control-plane surface.
    """

    parameters = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "app.mcp_stdio",
        ],
        cwd=str(
            PROJECT_ROOT
        ),
    )

    async with stdio_client(
        parameters
    ) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
        ) as session:
            await session.initialize()

            listed = await session.list_tools()

            tool_names = [
                tool.name
                for tool in listed.tools
            ]

            task_context_result = (
                await session.call_tool(
                    "toolfence.task_context",
                    arguments={},
                )
            )

            policy_status_result = (
                await session.call_tool(
                    "toolfence.policy_status",
                    arguments={},
                )
            )

            return (
                tool_names,
                _extract_structured_result(
                    task_context_result
                ),
                _extract_structured_result(
                    policy_status_result
                ),
            )


def test_real_stdio_server_exposes_expected_tools() -> None:
    tool_names, _, _ = asyncio.run(
        _inspect_control_plane()
    )

    assert len(tool_names) == 15

    assert set(
        tool_names
    ) == EXPECTED_TOOLS

    assert (
        "toolfence.task_context"
        in tool_names
    )


def test_task_context_exposes_only_canonical_identity() -> None:
    _, task_context, _ = asyncio.run(
        _inspect_control_plane()
    )

    assert task_context == {
        "task_id": "BUG-17-FIX",
        "task": (
            "Fix BUG-17, run CI, "
            "and create a pull request."
        ),
    }

    # The control-plane endpoint must not reveal
    # the trusted capability ceiling.
    assert set(
        task_context.keys()
    ) == {
        "task_id",
        "task",
    }


def test_fresh_server_has_trusted_approval_but_no_policy() -> None:
    _, _, policy_status = asyncio.run(
        _inspect_control_plane()
    )

    assert policy_status[
        "task_id"
    ] == "BUG-17-FIX"

    assert (
        policy_status[
            "approval_registered"
        ]
        is True
    )

    assert (
        policy_status[
            "policy_registered"
        ]
        is False
    )

    assert (
        policy_status[
            "active"
        ]
        is False
    )

    assert (
        policy_status[
            "state"
        ]
        == "UNREGISTERED"
    )

    assert (
        policy_status[
            "policy_id"
        ]
        is None
    )