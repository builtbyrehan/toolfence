"""An in-memory Ticket service for the ToolFence demo."""

from copy import deepcopy
from threading import RLock
from typing import TypedDict

from app.policy.matcher import validate_resource


MAX_COMMENT_LENGTH = 4000


class TicketRecord(TypedDict):
    ticket_id: str
    title: str
    description: str
    repository: str
    branch: str
    source_file: str
    test_file: str
    acceptance_criteria: list[str]
    comments: list[str]


class TicketService:
    """Provide ticket.get, ticket.comment, and ticket.delete operations."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._tickets: dict[str, TicketRecord] = {
            "BUG-17": {
                "ticket_id": "BUG-17",
                "title": "Cart total skips the first item",
                "description": (
                    "calculate_total(prices) skips the first cart item. "
                    "For [10, 20, 30], it returns 50 instead of 60. "
                    "Fix the implementation while preserving its signature."
                ),
                "repository": "project",
                "branch": "feature/BUG-17",
                "source_file": "project/src/cart.py",
                "test_file": "project/tests/test_cart.py",
                "acceptance_criteria": [
                    "The total includes every item in the input list.",
                    "An empty list returns 0.",
                    "A single-item list returns that item's price.",
                ],
                "comments": [],
            }
        }

    def _require_ticket(self, ticket_id: str) -> TicketRecord:
        """Return internal state; callers must hold the service lock."""
        try:
            return self._tickets[ticket_id]
        except KeyError:
            raise KeyError(f"Ticket not found: {ticket_id}") from None

    def get(self, ticket_id: str) -> TicketRecord:
        """Return a copy so callers cannot mutate stored ticket data."""
        validate_resource("ticket_id", ticket_id)

        with self._lock:
            return deepcopy(self._require_ticket(ticket_id))

    def comment(self, ticket_id: str, body: str) -> dict[str, object]:
        """Add a comment and return its ticket-local sequence number."""
        validate_resource("ticket_id", ticket_id)

        if not isinstance(body, str):
            raise ValueError("comment body must be a string")

        if not body.strip():
            raise ValueError("comment body must not be blank")

        if len(body) > MAX_COMMENT_LENGTH:
            raise ValueError(
                f"comment body must not exceed {MAX_COMMENT_LENGTH} characters"
            )

        with self._lock:
            ticket = self._require_ticket(ticket_id)
            ticket["comments"].append(body)

            return {
                "ticket_id": ticket_id,
                "comment_number": len(ticket["comments"]),
                "body": body,
            }

    def delete(self, ticket_id: str) -> dict[str, object]:
        """Remove a ticket from this service instance."""
        validate_resource("ticket_id", ticket_id)

        with self._lock:
            self._require_ticket(ticket_id)
            del self._tickets[ticket_id]

            return {"ticket_id": ticket_id, "deleted": True}

