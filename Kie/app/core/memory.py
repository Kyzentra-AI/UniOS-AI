from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class MemoryItem:
    """
    Represents a single piece of learner memory.

    Memory is categorized and associated with a learner
    so KIE can retrieve the correct long-term context.
    """

    category: str
    content: Any
    source: str = "kie"
    user_id: str = "default"
    created_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )


class MemoryEngine:
    """
    Sprint 3 Memory Engine.

    Supported memory categories:
    - preferences
    - conversations
    - learning_history
    - projects
    - goals
    - achievements
    - friction_context

    Memory is isolated by user_id.

    Persistent storage remains a Backend responsibility.
    """

    VALID_CATEGORIES = {
        "preferences",
        "conversations",
        "learning_history",
        "projects",
        "goals",
        "achievements",
        "friction_context",
    }

    DEFAULT_USER_ID = "default"

    def __init__(self):
        self._memory: dict[
            str,
            dict[str, list[MemoryItem]],
        ] = {}

    def store(
        self,
        category: str,
        content: Any,
        source: str = "kie",
        user_id: str = DEFAULT_USER_ID,
    ) -> MemoryItem:
        """
        Store a new memory item for a specific learner.
        """

        self._validate_category(category)

        self._ensure_user(user_id)

        item = MemoryItem(
            category=category,
            content=content,
            source=source,
            user_id=user_id,
        )

        self._memory[user_id][category].append(item)

        return item

    def update(
        self,
        category: str,
        content: Any,
        source: str = "kie",
        user_id: str = DEFAULT_USER_ID,
    ) -> MemoryItem:
        """
        Add a new learner memory item.

        KIE memory is append-only so learner history
        is preserved.
        """

        return self.store(
            category=category,
            content=content,
            source=source,
            user_id=user_id,
        )

    def resolve_update_category(
        self,
        task: str,
        intent: str,
    ) -> str:
        """
        Determine the memory category associated with
        a completed KIE request.

        Explicit learner-memory signals are classified
        into their appropriate categories.

        Normal KIE executions remain in learning_history
        so the existing Sprint 3 memory history behavior
        remains backward compatible.
        """

        task_lower = task.lower()

        # -------------------------------------------------
        # Explicit preference memory
        # -------------------------------------------------

        if any(
            phrase in task_lower
            for phrase in [
                "save my preference",
                "remember my preference",
                "my learning preference",
                "my learning style",
                "my study style",
                "i prefer",
            ]
        ):
            return "preferences"

        # -------------------------------------------------
        # Explicit project memory
        # -------------------------------------------------

        if any(
            phrase in task_lower
            for phrase in [
                "save this project",
                "remember this project",
                "project history",
                "project experience",
                "project achievement",
            ]
        ):
            return "projects"

        # -------------------------------------------------
        # Explicit goal memory
        # -------------------------------------------------

        if any(
            phrase in task_lower
            for phrase in [
                "save my goal",
                "remember my goal",
                "my career goal",
                "my learning goal",
                "set my goal",
                "set a goal",
            ]
        ):
            return "goals"

        # -------------------------------------------------
        # Explicit achievement memory
        # -------------------------------------------------

        if any(
            phrase in task_lower
            for phrase in [
                "save my achievement",
                "remember my achievement",
                "save this achievement",
                "certificate achievement",
                "achievement history",
            ]
        ):
            return "achievements"

        # -------------------------------------------------
        # Explicit friction memory
        # -------------------------------------------------

        if any(
            phrase in task_lower
            for phrase in [
                "i am stuck",
                "i'm stuck",
                "i am struggling",
                "i'm struggling",
                "i have difficulty",
                "i am confused",
                "i'm confused",
                "remember my difficulty",
                "remember my problem",
                "friction context",
            ]
        ):
            return "friction_context"

        # -------------------------------------------------
        # Learning activity
        # -------------------------------------------------

        if intent == "LEARN":
            return "learning_history"

        # -------------------------------------------------
        # Backward-compatible default
        # -------------------------------------------------

        return "learning_history"

    def retrieve(
        self,
        category: str | None = None,
        user_id: str = DEFAULT_USER_ID,
    ) -> list[MemoryItem]:
        """
        Retrieve memory for a specific learner.

        If category is provided, return only that category.

        If category is omitted, return all memory for the learner.
        """

        self._ensure_user(user_id)

        if category is not None:
            self._validate_category(category)

            return list(
                self._memory[user_id][category]
            )

        memories = []

        for items in self._memory[user_id].values():
            memories.extend(items)

        return memories

    def retrieve_relevant(
        self,
        categories: list[str],
        user_id: str = DEFAULT_USER_ID,
    ) -> dict[str, list[MemoryItem]]:
        """
        Retrieve selected memory categories for a specific learner.
        """

        self._ensure_user(user_id)

        result: dict[
            str,
            list[MemoryItem],
        ] = {}

        for category in categories:
            self._validate_category(category)

            result[category] = list(
                self._memory[user_id][category]
            )

        return result

    def clear(
        self,
        user_id: str | None = None,
    ) -> None:
        """
        Clear memory.

        If user_id is provided, clear only that learner's memory.

        If user_id is omitted, clear all learners' memory.
        """

        if user_id is None:
            self._memory.clear()
            return

        self._memory.pop(
            user_id,
            None,
        )

    def list_categories(self) -> list[str]:
        """
        Return supported memory categories.
        """

        return sorted(
            self.VALID_CATEGORIES
        )

    def list_users(self) -> list[str]:
        """
        Return learners currently represented in memory.
        """

        return list(
            self._memory.keys()
        )

    def _ensure_user(
        self,
        user_id: str,
    ) -> None:
        if not user_id:
            user_id = self.DEFAULT_USER_ID

        if user_id not in self._memory:
            self._memory[user_id] = {
                category: []
                for category in self.VALID_CATEGORIES
            }

    def _validate_category(
        self,
        category: str,
    ) -> None:
        if category not in self.VALID_CATEGORIES:
            raise ValueError(
                f"Unsupported memory category: {category}"
            )