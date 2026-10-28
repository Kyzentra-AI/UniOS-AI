from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TeachingStrategy(str, Enum):
    FOUNDATIONAL = "foundational"
    REINFORCEMENT = "reinforcement"
    ADVANCEMENT = "advancement"
    REMEDIATION = "remediation"
    # Canonical strategies from Universal Engineering Bible
    CONCEPT_FIRST = "concept_first"
    CASE_DRIVEN = "case_driven"
    PRACTICAL_FIRST = "practical_first"
    CHALLENGE_BASED = "challenge_based"


class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class PresentationMode(str, Enum):
    TRADITIONAL = "traditional"
    VISUAL = "visual"
    STORY = "story"
    SIMULATION = "simulation"
    ANIMATION = "animation"
    INTERACTIVE = "interactive"
    ANALYTICAL = "analytical"
    CASE_STUDY = "case_study"


class PracticeLevel(str, Enum):
    GUIDED = "guided"
    INDEPENDENT = "independent"
    CHALLENGE_BASED = "challenge_based"
    REMEDIAL = "remedial"


class PedagogyDecision(BaseModel):
    """The pedagogy strategy chosen for the learner and topic (A2-S4-01)."""

    strategy: TeachingStrategy
    difficulty: DifficultyLevel
    presentation_mode: PresentationMode
    explanation_depth: str = Field(
        description="Depth of explanation: high-level, step-by-step, or deep-dive"
    )
    rationale: str = Field(
        description="Pedagogical reasoning based on learner mastery and stage"
    )
    sequence: List[str] = Field(
        default_factory=lambda: [
            "explain_prerequisite",
            "explain_concept",
            "show_example",
            "guided_practice",
            "assessment",
        ],
        description="Ordered sequence of pedagogical steps",
    )
    practice_level: PracticeLevel = Field(
        default=PracticeLevel.GUIDED,
        description="Practice approach calibrated to learner confidence and mastery",
    )
    remediation: bool = Field(
        default=False,
        description="Whether this decision represents an active remediation intervention",
    )
    recommended_level: Optional[str] = Field(
        default=None,
        description="Recommended level indicator (beginner, intermediate, advanced)",
    )
    reasoning_summary: Optional[str] = Field(
        default=None,
        description="Canonical reasoning summary alias for KIE contract",
    )

    def model_post_init(self, __context):
        if self.reasoning_summary is None and self.rationale:
            self.reasoning_summary = self.rationale
        if self.recommended_level is None and self.difficulty:
            self.recommended_level = self.difficulty.value

