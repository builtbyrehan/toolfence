"""Match ToolFence's logical resource names and permission scopes.

MVP resources use case-sensitive ASCII names and forward slashes.
Repository adapters must separately enforce filesystem containment.
"""

import re

from app.policy.schema import ResourceType


_COMPONENT = re.compile(r"[A-Za-z0-9_.-]+")
_FLAT_TYPES = frozenset({"ticket_id", "environment", "secret_id"})
_KNOWN_TYPES = _FLAT_TYPES | {"repo_path", "branch"}
_MAX_RESOURCE_LENGTH = 512


def _validate_type(resource_type: ResourceType) -> None:
    if not isinstance(resource_type, str) or resource_type not in _KNOWN_TYPES:
        raise ValueError("unsupported resource type")


def _validate_parts(value: str) -> tuple[str, ...]:
    if not isinstance(value, str):
        raise ValueError("resource must be a string")

    if not 1 <= len(value) <= _MAX_RESOURCE_LENGTH:
        raise ValueError("resource length must be between 1 and 512 characters")

    parts = tuple(value.split("/"))

    for part in parts:
        if part in {".", ".."}:
            raise ValueError("dot and parent-directory segments are forbidden")

        if not _COMPONENT.fullmatch(part):
            raise ValueError(
                "resource segments must use ASCII letters, digits, dots, "
                "underscores, or hyphens"
            )

        if part.endswith("."):
            raise ValueError("resource segments must not end with a dot")

    return parts


def validate_resource(resource_type: ResourceType, resource: str) -> str:
    """Validate a concrete resource and return it unchanged."""
    _validate_type(resource_type)
    parts = _validate_parts(resource)

    if resource_type in _FLAT_TYPES and len(parts) != 1:
        raise ValueError("this resource type requires a single identifier")

    if resource_type == "repo_path" and len(parts) < 2:
        raise ValueError("repository resources require a repository and a path")

    return resource


def validate_resource_pattern(
    resource_type: ResourceType,
    pattern: str,
) -> str:
    """Allow exact resources, plus a trailing /* for repository subtrees."""
    _validate_type(resource_type)

    if (
        resource_type == "repo_path"
        and isinstance(pattern, str)
        and pattern.endswith("/*")
    ):
        if len(pattern) > _MAX_RESOURCE_LENGTH:
            raise ValueError("resource pattern must not exceed 512 characters")

        _validate_parts(pattern[:-2])
        return pattern

    return validate_resource(resource_type, pattern)


def resource_matches(
    resource_type: ResourceType,
    pattern: str,
    resource: str,
) -> bool:
    """Return whether a permission covers a concrete resource.

    A repository scope ending in /* covers all descendants, at any depth.
    Invalid inputs never match.
    """
    try:
        validate_resource_pattern(resource_type, pattern)
        validate_resource(resource_type, resource)
    except (TypeError, ValueError):
        return False

    if resource_type == "repo_path" and pattern.endswith("/*"):
        # Keep the slash so project/src/* cannot match project/src_backup.
        return resource.startswith(pattern[:-1])

    return resource == pattern


def scope_covers(
    resource_type: ResourceType,
    approved_scope: str,
    requested_scope: str,
) -> bool:
    """Return whether a requested scope stays inside an approved scope."""
    try:
        validate_resource_pattern(resource_type, approved_scope)
        validate_resource_pattern(resource_type, requested_scope)
    except (TypeError, ValueError):
        return False

    if approved_scope == requested_scope:
        return True

    if resource_type != "repo_path" or not approved_scope.endswith("/*"):
        return False

    approved_prefix = approved_scope[:-1]

    if requested_scope.endswith("/*"):
        requested_root = requested_scope[:-2]
        return requested_root.startswith(approved_prefix)

    return requested_scope.startswith(approved_prefix)