from pydantic import BaseModel, Field


class SyllabusExtractRequest(BaseModel):
    """
    Request sent by Backend to extract structured
    subjects and topics from raw syllabus text.
    """

    syllabus_id: str = Field(
        ...,
        min_length=1,
    )

    text: str = Field(
        ...,
        min_length=1,
    )


class SyllabusSubject(BaseModel):
    """
    One subject and its extracted topics.
    """

    name: str = Field(
        ...,
        min_length=1,
    )

    topics: list[str] = Field(
        default_factory=list,
    )


class SyllabusExtractResponse(BaseModel):
    """
    Structured syllabus returned to Backend.
    """

    subjects: list[SyllabusSubject] = Field(
        default_factory=list,
    )