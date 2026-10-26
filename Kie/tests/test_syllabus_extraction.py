
from app.core.syllabus import SyllabusExtractionEngine
from app.schemas.syllabus import SyllabusExtractRequest


def make_request(text: str) -> SyllabusExtractRequest:
    return SyllabusExtractRequest(
        syllabus_id="test-syllabus-001",
        text=text,
    )


def test_extracts_subject_and_topics_from_multiline_text():
    engine = SyllabusExtractionEngine()

    result = engine.extract(
        make_request(
            "Database Management Systems:\n"
            "- Relational Algebra\n"
            "- SQL\n"
            "- Normalization\n"
        )
    )

    assert len(result["subjects"]) == 1
    assert result["subjects"][0]["name"] == "Database Management Systems"
    assert result["subjects"][0]["topics"] == [
        "Relational Algebra",
        "SQL",
        "Normalization",
    ]


def test_extracts_topics_from_escaped_newlines():
    engine = SyllabusExtractionEngine()

    result = engine.extract(
        make_request(
            r"Database Management Systems:\n"
            r"Relational Algebra\n"
            r"SQL\n"
            r"Normalization"
        )
    )

    assert len(result["subjects"]) == 1
    assert result["subjects"][0]["name"] == "Database Management Systems"
    assert "SQL" in result["subjects"][0]["topics"]
    assert "Normalization" in result["subjects"][0]["topics"]


def test_recognizes_unit_headings():
    engine = SyllabusExtractionEngine()

    result = engine.extract(
        make_request(
            "UNIT I: Relational Model\n"
            "Relational Algebra\n"
            "SQL\n"
            "UNIT II: Database Design\n"
            "Normalization\n"
            "Functional Dependencies\n"
        )
    )

    assert len(result["subjects"]) == 2
    assert result["subjects"][0]["name"] == "Unit I: Relational Model"
    assert "Relational Algebra" in result["subjects"][0]["topics"]
    assert result["subjects"][1]["name"] == "Unit II: Database Design"
    assert "Normalization" in result["subjects"][1]["topics"]


def test_preserves_content_when_no_heading_is_recognized():
    engine = SyllabusExtractionEngine()

    result = engine.extract(
        make_request(
            "Relational Algebra\n"
            "SQL\n"
            "Normalization"
        )
    )

    assert len(result["subjects"]) == 1
    assert result["subjects"][0]["name"] == "Syllabus Topics"
    assert result["subjects"][0]["topics"] == [
        "Relational Algebra",
        "SQL",
        "Normalization",
    ]


def test_duplicate_topics_are_removed():
    engine = SyllabusExtractionEngine()

    result = engine.extract(
        make_request(
            "Database Management Systems:\n"
            "SQL\n"
            "Normalization\n"
            "SQL\n"
        )
    )

    assert result["subjects"][0]["topics"] == [
        "SQL",
        "Normalization",
    ]
