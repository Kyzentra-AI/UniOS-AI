from typing import Any, ClassVar

from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_validator,
)


class RoadmapMilestone(BaseModel):
    """
    Represents one generated roadmap milestone.

    KIE generates the milestone.

    Backend is responsible for persistent storage
    and future milestone state updates.
    """

    milestone_id: str

    description: str

    agent: str | None = None

    status: str = "planned"

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)


class RoadmapContract(BaseModel):
    """
    Structured Sprint 3 roadmap integration contract.

    KIE generates this contract from the Planning Engine.

    Backend consumes the contract and owns:

    - persistent storage
    - retrieval
    - updates
    - synchronization
    """

    VALID_HORIZONS: ClassVar[set[str]] = {
        "semester",
        "career",
        "monthly",
        "weekly",
        "daily",
        "mission",
    }

    user_id: str

    session_id: str

    planning_horizon: str | None = None

    learner_stage: str | None = None

    career_goal: str | None = None

    milestones: list[RoadmapMilestone] = Field(
        default_factory=list
    )

    milestone_count: int = Field(
        ge=0
    )

    planning_status: str

    @field_validator("planning_horizon")
    @classmethod
    def validate_planning_horizon(
        cls,
        value: str | None,
    ) -> str | None:
        if value is None:
            return value

        value = value.strip().lower()

        if value not in cls.VALID_HORIZONS:
            raise ValueError(
                "Unsupported planning horizon: "
                f"{value}"
            )

        return value

    @model_validator(mode="after")
    def validate_milestone_count(self):
        """
        Ensure the declared milestone count
        matches the actual number of milestones.
        """

        if self.milestone_count != len(
            self.milestones
        ):
            raise ValueError(
                "milestone_count must match "
                "the number of milestones"
            )

        return self

    def __getitem__(self, key: str) -> Any:
        return getattr(self, key)