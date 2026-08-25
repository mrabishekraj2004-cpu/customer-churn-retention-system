from src.database.models import RetentionAction
from src.database.repositories import RetentionActionRepository


class RetentionActionNotFoundError(Exception):
    """Raised when a requested retention action does not exist."""


class InvalidRetentionActionUpdateError(Exception):
    """Raised when a retention action update violates workflow rules."""


class RetentionActionService:
    """Manage retention-action retrieval and lifecycle updates."""

    def __init__(
        self,
        repository: RetentionActionRepository,
    ) -> None:
        self.repository = repository

    def get_actions(
        self,
        limit: int = 100,
        offset: int = 0,
        status: str | None = None,
    ) -> list[RetentionAction]:
        return self.repository.get_all(
            limit=limit,
            offset=offset,
            status=status,
        )

    def get_action(
        self,
        action_id: int,
    ) -> RetentionAction:
        action = self.repository.get_by_id(action_id)

        if action is None:
            raise RetentionActionNotFoundError(
                f"Retention action not found: {action_id}"
            )

        return action

    def update_action(
        self,
        action_id: int,
        status: str,
        outcome: str | None = None,
    ) -> RetentionAction:
        action = self.get_action(action_id)

        self._validate_transition(
            current_status=action.status,
            new_status=status,
            outcome=outcome,
        )

        return self.repository.update_status(
            action=action,
            status=status,
            outcome=outcome,
        )

    @staticmethod
    def _validate_transition(
        current_status: str,
        new_status: str,
        outcome: str | None,
    ) -> None:
        allowed_transitions = {
            "recommended": {
                "recommended",
                "in_progress",
            },
            "in_progress": {
                "in_progress",
                "completed",
            },
            "completed": {
                "completed",
            },
        }

        if current_status not in allowed_transitions:
            raise InvalidRetentionActionUpdateError(
                f"Unknown retention action status: {current_status}"
            )

        if new_status not in allowed_transitions[current_status]:
            raise InvalidRetentionActionUpdateError(
                f"Cannot change retention action from "
                f"{current_status} to {new_status}."
            )

        if new_status == "completed" and outcome is None:
            raise InvalidRetentionActionUpdateError(
                "An outcome is required when completing "
                "a retention action."
            )

        if new_status != "completed" and outcome is not None:
            raise InvalidRetentionActionUpdateError(
                "Outcome can only be provided for a completed "
                "retention action."
            )