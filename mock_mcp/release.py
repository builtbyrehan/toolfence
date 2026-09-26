from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import TypedDict

from app.policy.matcher import validate_resource


MAX_VERSION_LENGTH = 128

SUPPORTED_ENVIRONMENTS = (
    "staging",
    "production",
)


class ReleaseStatusRecord(TypedDict):
    environment: str
    deployed_version: str
    deployment_count: int


class DeploymentRecord(TypedDict):
    deployment_id: int
    environment: str
    previous_version: str
    deployed_version: str
    status: str


_INITIAL_RELEASES: dict[str, str] = {
    "staging": "demo-1.0.0",
    "production": "demo-1.0.0",
}


class ReleaseService:
    """
    Small in-memory release backend for the ToolFence demo.

    This class deliberately does not perform authorization.

    The future ToolFence protected execution layer is responsible for
    deciding whether release.status or release.deploy is allowed before
    invoking this service.
    """

    def __init__(self) -> None:
        self._lock = RLock()

        self._versions: dict[str, str] = deepcopy(_INITIAL_RELEASES)

        self._deployment_counts: dict[str, int] = {
            environment: 0
            for environment in SUPPORTED_ENVIRONMENTS
        }

        self._deployment_history: list[DeploymentRecord] = []

    def status(self, environment: str) -> ReleaseStatusRecord:
        """
        Return the current release status for an environment.

        Raises:
            ValueError:
                If the environment resource identifier is malformed.

            KeyError:
                If the environment does not exist.
        """
        self._validate_environment(environment)

        with self._lock:
            return {
                "environment": environment,
                "deployed_version": self._versions[environment],
                "deployment_count": self._deployment_counts[environment],
            }

    def deploy(
        self,
        environment: str,
        version: str,
    ) -> DeploymentRecord:
        """
        Deploy a version to an environment.

        The deployment updates the in-memory release state and records
        a deployment-history entry.

        Raises:
            ValueError:
                If the environment identifier or version is invalid.

            KeyError:
                If the environment does not exist.
        """
        self._validate_environment(environment)
        self._validate_version(version)

        with self._lock:
            previous_version = self._versions[environment]

            deployment_id = len(self._deployment_history) + 1

            record: DeploymentRecord = {
                "deployment_id": deployment_id,
                "environment": environment,
                "previous_version": previous_version,
                "deployed_version": version,
                "status": "deployed",
            }

            self._versions[environment] = version
            self._deployment_counts[environment] += 1
            self._deployment_history.append(deepcopy(record))

            return deepcopy(record)

    def deployment_history(self) -> list[DeploymentRecord]:
        """
        Return safe copies of every deployment recorded by this service.
        """
        with self._lock:
            return deepcopy(self._deployment_history)

    def _validate_environment(self, environment: str) -> None:
        validate_resource("environment", environment)

        if environment not in self._versions:
            raise KeyError(
                f"Unknown release environment: {environment}"
            )

    @staticmethod
    def _validate_version(version: str) -> None:
        if not isinstance(version, str):
            raise ValueError("Release version must be a string.")

        if not version.strip():
            raise ValueError("Release version cannot be blank.")

        if version != version.strip():
            raise ValueError(
                "Release version cannot contain surrounding whitespace."
            )

        if len(version) > MAX_VERSION_LENGTH:
            raise ValueError(
                "Release version exceeds the maximum length of "
                f"{MAX_VERSION_LENGTH} characters."
            )

        if any(not character.isprintable() for character in version):
            raise ValueError(
                "Release version cannot contain nonprintable characters."
            )