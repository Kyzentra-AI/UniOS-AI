
import json
from typing import Any

from app.core.model_router import ModelRouter
from app.schemas.career import ResumeGenerateRequest, ResumeGenerateResponse


class ResumeGenerationError(Exception):
    """Raised when resume generation fails."""


class ResumeGenerationEngine:
    """Generate structured ATS-friendly resume content using Ollama."""

    def __init__(self, model_router: ModelRouter | None = None):
        self.model_router = model_router or ModelRouter()

    def generate(
        self,
        request: ResumeGenerateRequest,
    ) -> ResumeGenerateResponse:
        system_prompt = (
            "You are a professional ATS resume writing assistant. "
            "Create accurate, ATS-friendly resume content using only "
            "the information supplied by the user. "
            "Never invent employers, dates, qualifications, metrics, "
            "certifications, projects, or achievements. "
            "Use clear headings, relevant keywords, and concise bullets. "
            "Do not include tables, icons, graphics, or columns. "
            "Return ONLY a valid JSON object with these keys: "
            "professional_summary (string), "
            "skills (array of strings), "
            "experience (array of objects), "
            "projects (array of objects), "
            "education (array of objects), "
            "certifications (array of strings). "
            "Do not wrap JSON in markdown code fences."
        )

        prompt_data: dict[str, Any] = {
            "title": request.title,
            "source": request.source,
            "target_role": request.preferences.targetRole,
            "tone": request.preferences.tone,
            "profile_content": request.content,
            "career_context": request.career_context,
        }

        prompt = (
            "Generate an ATS-friendly resume from this information:\n"
            + json.dumps(prompt_data, ensure_ascii=False)
        )

        try:
            result = self.model_router.generate(
                prompt=prompt,
                system=system_prompt,
                capability="general",
            )

            raw_content = result["content"].strip()

            if raw_content.startswith("```"):
                raw_content = raw_content.split("\n", 1)[-1]
                raw_content = raw_content.rsplit("```", 1)[0].strip()

            resume_content = json.loads(raw_content)

            if not isinstance(resume_content, dict):
                raise ValueError("Resume response must be a JSON object.")

            required_fields = {
                "professional_summary",
                "skills",
                "experience",
                "projects",
                "education",
                "certifications",
            }

            if not required_fields.issubset(resume_content):
                raise ValueError(
                    "Resume response is missing required sections."
                )

            return ResumeGenerateResponse(content=resume_content)

        except (ValueError, KeyError, TypeError) as exc:
            raise ResumeGenerationError(
                "The LLM returned an invalid resume structure."
            ) from exc
        except Exception as exc:
            raise ResumeGenerationError(
                "Resume generation failed."
            ) from exc
