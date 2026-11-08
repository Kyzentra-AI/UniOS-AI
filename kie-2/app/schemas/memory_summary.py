from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MemorySummaryRequest(BaseModel):
    """Inbound request from Backend: POST /api/v1/kie/memory/summary"""
    model_config = ConfigDict(extra="allow")

    events: List[Dict[str, Any]] = Field(default_factory=list, description="Recent learner events")


class MemorySummaryResponse(BaseModel):
    """
    Opaque JSON summary returned to Backend for ContextV2Assembler.
    Backend treats this as Dict[str, Any].
    """
    model_config = ConfigDict(extra="allow")

    mastered_concepts: List[str] = Field(default_factory=list)
    struggling_concepts: List[str] = Field(default_factory=list)
    recommended_pacing: str = Field(default="Moderate with scaffolding")
    recent_activity_summary: str = Field(default="No recent learner events recorded.")
    engagement_level: str = Field(default="normal")

