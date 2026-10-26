
import re

from app.schemas.syllabus import SyllabusExtractRequest


class SyllabusExtractionEngine:
    """Extract structured subjects and topics from syllabus text."""

    SUBJECT_KEYWORDS = {
        "data structures",
        "algorithms",
        "operating systems",
        "database management systems",
        "dbms",
        "computer networks",
        "software engineering",
        "machine learning",
        "deep learning",
        "artificial intelligence",
        "web development",
        "computer architecture",
        "object oriented programming",
        "relational model",
    }

    UNIT_PATTERN = re.compile(
        r"^(UNIT|MODULE|CHAPTER)\s+"
        r"([IVXLCDM]+|\d+)\s*[:.\-–—]?\s*(.*)$",
        re.IGNORECASE,
    )

    def extract(self, request: SyllabusExtractRequest) -> dict:
        text = self._normalize_text(request.text)
        return {"subjects": self._extract_subjects(text)}

    @staticmethod
    def _normalize_text(text: str) -> str:
        # Convert escaped line separators into actual line breaks.
        text = (
            text.replace("\\r\\n", "\n")
            .replace("\\n", "\n")
            .replace("\\r", "\n")
            .replace("\\t", "\t")
        )
        return text.strip()

    def _extract_subjects(self, text: str) -> list[dict]:
        lines = [
            self._clean_line(line)
            for line in text.splitlines()
        ]
        lines = [line for line in lines if line]

        subjects: list[dict] = []
        current_subject: dict | None = None
        ungrouped_topics: list[str] = []

        for line in lines:
            unit_match = self.UNIT_PATTERN.match(line)

            if unit_match:
                if current_subject is not None:
                    self._append_subject(subjects, current_subject)

                unit_type, unit_number, title = unit_match.groups()
                name = f"{unit_type.title()} {unit_number}"
                title = title.strip().rstrip(":").strip()

                if title:
                    name = f"{name}: {title}"

                current_subject = {"name": name, "topics": []}
                continue

            if self._looks_like_subject(line):
                if current_subject is not None:
                    self._append_subject(subjects, current_subject)

                current_subject = {
                    "name": line.rstrip(":").strip(),
                    "topics": [],
                }
                continue

            # If there is no heading yet, preserve content rather than
            # silently returning an empty subject list.
            topic = self._clean_topic(line)
            if not topic:
                continue

            if current_subject is None:
                ungrouped_topics.append(topic)
            elif topic.casefold() not in {
                item.casefold() for item in current_subject["topics"]
            }:
                current_subject["topics"].append(topic)

        if current_subject is not None:
            self._append_subject(subjects, current_subject)

        if not subjects and ungrouped_topics:
            subjects.append({
                "name": "Syllabus Topics",
                "topics": self._unique(ungrouped_topics),
            })

        return subjects

    @staticmethod
    def _append_subject(subjects: list[dict], subject: dict) -> None:
        if subject["name"]:
            subject["topics"] = SyllabusExtractionEngine._unique(
                subject["topics"]
            )
            subjects.append(subject)

    @staticmethod
    def _clean_line(line: str) -> str:
        line = line.strip()
        # Remove common bullets and numbered list prefixes.
        line = re.sub(
            r"^\s*(?:[-*•]|â€¢|\d+[\.\)])\s*",
            "",
            line,
        )
        return line.strip()

    @staticmethod
    def _clean_topic(line: str) -> str:
        return re.sub(r"\s+", " ", line).strip().rstrip(";").strip()

    @classmethod
    def _looks_like_subject(cls, line: str) -> bool:
        normalized = line.lower().strip().rstrip(":").strip()

        if normalized in cls.SUBJECT_KEYWORDS:
            return True

        # A short, standalone colon-terminated line can be a heading.
        if line.endswith(":") and len(line) <= 100:
            return True

        return False

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        result = []
        seen = set()

        for value in values:
            normalized = value.casefold()
            if normalized not in seen:
                seen.add(normalized)
                result.append(value)

        return result
