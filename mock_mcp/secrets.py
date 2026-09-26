from __future__ import annotations

from copy import deepcopy
from threading import RLock
from typing import TypedDict

from app.policy.matcher import validate_resource


class SecretRecord(TypedDict):
    secret_id: str
    value: str
    description: str


_INITIAL_SECRETS: dict[str, SecretRecord] = {
    "production-key": {
        "secret_id": "production-key",
        "value": "DEMO_ONLY_NOT_A_REAL_PRODUCTION_SECRET",
        "description": "Fake production credential used only by the ToolFence demo.",
    },
    "staging-key": {
        "secret_id": "staging-key",
        "value": "DEMO_ONLY_NOT_A_REAL_STAGING_SECRET",
        "description": "Fake staging credential used only by the ToolFence demo.",
    },
}


class SecretService:
    """
    Small in-memory secrets backend for the ToolFence golden demo.

    All stored values are intentionally fake.

    This service deliberately does not perform authorization. The future
    ToolFence protected execution layer must authorize secret.read before
    invoking this backend.
    """

    def __init__(self) -> None:
        self._lock = RLock()
        self._secrets: dict[str, SecretRecord] = deepcopy(_INITIAL_SECRETS)

    def read(self, secret_id: str) -> SecretRecord:
        """
        Return a fake demo secret.

        Raises:
            ValueError:
                If the logical secret identifier is malformed.

            KeyError:
                If the requested secret does not exist.
        """
        validate_resource("secret_id", secret_id)

        with self._lock:
            if secret_id not in self._secrets:
                raise KeyError(f"Secret does not exist: {secret_id}")

            return deepcopy(self._secrets[secret_id])