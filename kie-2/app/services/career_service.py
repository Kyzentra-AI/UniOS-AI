"""
UniOS Sprint 7 — Career Intelligence & ATS Service (AI/ML-2 KIE)
Tasks:
  - BE-S7-01 & BE-S7-04: AI Resume Generator (POST /api/v1/kie/career/resume/generate)
  - ATS Resume Checker Qualitative Refinement (POST /api/v1/kie/career/ats/analyze)

ARCHITECTURAL BOUNDARIES & INVARIANTS:
  - Backend owns authoritative persistence, database models, and artifact storage.
  - AI/ML-2 (KIE) owns stateless generative resume tailoring, alignment, and qualitative ATS refinement.
  - Zero database access, ORM dependencies, or external client libraries.
  - Grounding & Anti-Hallucination:
      * Missing contact information remains null; never invented or fabricated.
      * Whitelists of employers, institutions, and projects are strictly respected.
      * Original education, experience, project, and achievement IDs are preserved.
  - ATS Deterministic Boundary:
      * Deterministic rule score and methodology are preserved; LLM cannot alter or override them.
      * Original rule finding IDs and count are strictly preserved; findings are never dropped.
  - Error Safety:
      * Client-facing errors never leak API keys, auth tokens, or sensitive credentials.
      * Conforms to LLMProviderError and LLMParseError exception conventions.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ValidationError

from app.schemas.career import (
    ATSAnalyzeRequest,
    ATSAnalyzeResponse,
    ATSFindingSeverity,
    ResumeDraft,
    ResumeGenerateRequest,
    ResumeGenerateResponse,
    RuleFinding,
)
from app.services.career_prompt_builder import (
    build_ats_analysis_prompt,
    build_resume_generation_prompt,
)
from app.services.llm_provider import (
    BaseLLMProvider,
    LLMParseError,
    LLMProviderError,
    extract_json_payload,
    get_llm_provider,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Security & Sanitization Helpers
# ---------------------------------------------------------------------------

def _sanitize_error_message(message: str) -> str:
    """
    Strips raw API keys, bearer tokens, or sensitive credentials from error messages
    to prevent credential leakage in client-facing exceptions.
    """
    if not message:
        return ""
    # Strip Groq / OpenAI style API keys (e.g., gsk_..., sk-...)
    sanitized = re.sub(r"\bgsk_[A-Za-z0-9_-]{16,}\b", "[REDACTED_API_KEY]", message)
    sanitized = re.sub(r"\bsk-[A-Za-z0-9_-]{16,}\b", "[REDACTED_API_KEY]", sanitized)
    # Strip Authorization Bearer headers
    sanitized = re.sub(r"Bearer\s+[A-Za-z0-9_\-\.]{12,}", "Bearer [REDACTED]", sanitized, flags=re.IGNORECASE)
    # Strip key=... or api_key=... patterns
    sanitized = re.sub(r"(?:api[-_]?key|secret|token)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}['\"]?", "api_key=[REDACTED]", sanitized, flags=re.IGNORECASE)
    return sanitized


# ---------------------------------------------------------------------------
# Career Service Implementation
# ---------------------------------------------------------------------------

class CareerService:
    """
    Service layer orchestrating AI Resume Generation and ATS Feedback Refinement.
    Connects validated Pydantic contracts, grounding prompt builders, and LLM providers.
    """

    def __init__(self, provider: Optional[BaseLLMProvider] = None) -> None:
        self._provider = provider or get_llm_provider()

    # -----------------------------------------------------------------------
    # Provider Invocation & Safe Parsing
    # -----------------------------------------------------------------------

    def _invoke_provider(self, prompt: str) -> Any:
        """
        Invokes LLM provider abstraction defensively.
        Sanitizes provider exceptions so sensitive keys are never exposed.
        """
        try:
            if hasattr(self._provider, "generate_career_response"):
                return self._provider.generate_career_response(prompt)
            elif hasattr(self._provider, "generate_career_completion"):
                return self._provider.generate_career_completion(prompt)
            elif hasattr(self._provider, "generate_build_coaching"):
                return self._provider.generate_build_coaching(prompt)
            elif callable(self._provider):
                return self._provider(prompt)
            else:
                raise LLMProviderError("Configured LLM provider does not expose a supported generation method.")
        except LLMProviderError as err:
            sanitized_msg = _sanitize_error_message(str(err.message or str(err)))
            if isinstance(err, LLMParseError):
                sanitized_raw = _sanitize_error_message(err.raw_content) if err.raw_content else None
                raise LLMParseError(sanitized_msg, raw_content=sanitized_raw, status_code=err.status_code)
            raise LLMProviderError(sanitized_msg, status_code=err.status_code)
        except Exception as err:
            sanitized_msg = _sanitize_error_message(f"LLM provider invocation failed: {str(err)}")
            raise LLMProviderError(sanitized_msg, status_code=502)

    def _parse_provider_output(self, raw: Any) -> Dict[str, Any]:
        """
        Defensively parses structured JSON output from varied provider response formats.
        Supports:
          - dict (direct object)
          - str (raw JSON text or markdown code fence)
          - bytes (UTF-8 encoded JSON string)
          - BaseModel (Pydantic model instance)
        Raises LLMParseError on empty output or invalid JSON.
        """
        if raw is None:
            raise LLMParseError("LLM provider returned empty response (None).")

        if isinstance(raw, dict):
            if not raw:
                raise LLMParseError("LLM provider returned empty dictionary.")
            return raw

        if isinstance(raw, BaseModel):
            return raw.model_dump()

        if isinstance(raw, (bytes, bytearray)):
            try:
                raw = raw.decode("utf-8")
            except Exception as e:
                raise LLMParseError(f"Failed to decode provider bytes as UTF-8: {e}")

        if isinstance(raw, str):
            cleaned = raw.strip()
            if not cleaned:
                raise LLMParseError("LLM provider returned empty text response.")
            json_text = extract_json_payload(cleaned)
            try:
                parsed = json.loads(json_text)
                if not isinstance(parsed, dict):
                    raise LLMParseError(
                        f"Expected JSON object dictionary from LLM, got {type(parsed).__name__}.",
                        raw_content=cleaned,
                    )
                return parsed
            except json.JSONDecodeError as err:
                raise LLMParseError(
                    f"Malformed JSON returned by LLM: {str(err)}",
                    raw_content=cleaned,
                )

        raise LLMParseError(f"Unsupported LLM provider response type: {type(raw).__name__}")

    # -----------------------------------------------------------------------
    # 1. Resume Generation
    # -----------------------------------------------------------------------

    def generate_resume(self, request: ResumeGenerateRequest) -> ResumeGenerateResponse:
        """
        Synthesizes and tailors a professionally grounded resume draft.

        Pipeline:
          1. Validates input request.
          2. Builds grounding prompt via existing build_resume_generation_prompt.
          3. Invokes LLM provider through abstraction.
          4. Defensively parses structured response.
          5. Enforces strict anti-hallucination guardrails and ID preservation.
          6. Validates against ResumeDraft schema.
          7. Returns ResumeGenerateResponse(content=...).
        """
        if isinstance(request, dict):
            request = ResumeGenerateRequest.model_validate(request)
        elif not isinstance(request, ResumeGenerateRequest):
            raise ValueError("request must be an instance of ResumeGenerateRequest.")

        # 1. Build prompt using existing prompt builder (never duplicate prompt logic)
        prompt = build_resume_generation_prompt(request)

        # 2. Invoke LLM provider
        raw_output = self._invoke_provider(prompt)

        # 3. Parse JSON safely
        data = self._parse_provider_output(raw_output)

        # 4. Anti-hallucination & Grounding Guardrails:
        # Prevent fabricated contact details: if contact detail was not in base draft, keep None.
        base_contact = request.content.contact
        contact_data = data.get("contact")
        if not isinstance(contact_data, dict):
            contact_data = {}

        if base_contact:
            # Preserve original full name if present
            if base_contact.full_name:
                contact_data["full_name"] = base_contact.full_name
                contact_data["fullName"] = base_contact.full_name
            # Prevent hallucinated phone
            if not base_contact.phone:
                contact_data["phone"] = None
            # Prevent hallucinated email
            if not base_contact.email:
                contact_data["email"] = None
            # Prevent hallucinated URLs
            if not base_contact.linkedin_url:
                contact_data["linkedin_url"] = None
                contact_data["linkedInUrl"] = None
            if not base_contact.github_url:
                contact_data["github_url"] = None
                contact_data["githubUrl"] = None
            if not base_contact.portfolio_url:
                contact_data["portfolio_url"] = None
                contact_data["portfolioUrl"] = None
            if not base_contact.location:
                contact_data["location"] = None
        else:
            contact_data = {
                "full_name": None,
                "email": None,
                "phone": None,
                "location": None,
                "linkedin_url": None,
                "github_url": None,
                "portfolio_url": None,
            }
        data["contact"] = contact_data

        # Prevent fabricated empty sections:
        # If the candidate has 0 experience entries, do NOT invent work experience.
        if not request.content.experience:
            data["experience"] = []
        else:
            # Preserve existing experience IDs
            orig_exp_ids = [e.id for e in request.content.experience if e.id]
            if orig_exp_ids and isinstance(data.get("experience"), list):
                for idx, exp_item in enumerate(data["experience"]):
                    if isinstance(exp_item, dict) and idx < len(orig_exp_ids):
                        if not exp_item.get("id") or exp_item.get("id") not in orig_exp_ids:
                            exp_item["id"] = orig_exp_ids[idx]

        # If candidate has 0 education and career context has no education, do NOT invent degrees.
        has_context_edu = bool(
            request.career_context
            and request.career_context.education
            and request.career_context.education.university
        )
        if not request.content.education and not has_context_edu:
            data["education"] = []
        else:
            # Preserve existing education IDs
            orig_edu_ids = [e.id for e in request.content.education if e.id]
            if orig_edu_ids and isinstance(data.get("education"), list):
                for idx, edu_item in enumerate(data["education"]):
                    if isinstance(edu_item, dict) and idx < len(orig_edu_ids):
                        if not edu_item.get("id") or edu_item.get("id") not in orig_edu_ids:
                            edu_item["id"] = orig_edu_ids[idx]

        # If candidate has 0 projects and career context has no projects, do NOT invent projects.
        has_context_proj = bool(
            request.career_context
            and request.career_context.career_readiness
            and request.career_context.career_readiness.projects
        )
        if not request.content.projects and not has_context_proj:
            data["projects"] = []
        else:
            # Preserve existing project IDs
            orig_proj_ids = [p.id for p in request.content.projects if p.id]
            if orig_proj_ids and isinstance(data.get("projects"), list):
                for idx, proj_item in enumerate(data["projects"]):
                    if isinstance(proj_item, dict) and idx < len(orig_proj_ids):
                        if not proj_item.get("id") or proj_item.get("id") not in orig_proj_ids:
                            proj_item["id"] = orig_proj_ids[idx]

        # If candidate has 0 achievements, do NOT invent achievements.
        if not request.content.achievements:
            data["achievements"] = []
        else:
            orig_ach_ids = [a.id for a in request.content.achievements if a.id]
            if orig_ach_ids and isinstance(data.get("achievements"), list):
                for idx, ach_item in enumerate(data["achievements"]):
                    if isinstance(ach_item, dict) and idx < len(orig_ach_ids):
                        if not ach_item.get("id") or ach_item.get("id") not in orig_ach_ids:
                            ach_item["id"] = orig_ach_ids[idx]

        # 5. Schema validation against ResumeDraft
        try:
            draft = ResumeDraft.model_validate(data)
        except ValidationError as val_err:
            raise LLMParseError(
                f"Generated resume output failed schema validation: {str(val_err)}",
                raw_content=str(raw_output),
                status_code=502,
            )

        return ResumeGenerateResponse(content=draft)

    # Alias for flexibility
    generate_resume_draft = generate_resume

    # -----------------------------------------------------------------------
    # 2. ATS Analysis Feedback Refinement
    # -----------------------------------------------------------------------

    def analyze_ats(self, request: ATSAnalyzeRequest) -> ATSAnalyzeResponse:
        """
        Enriches deterministic ATS findings with qualitative, actionable feedback.

        Pipeline:
          1. Validates input request.
          2. Builds ATS refinement prompt via existing build_ats_analysis_prompt.
          3. Invokes LLM provider through abstraction.
          4. Defensively parses structured response.
          5. Preserves deterministic rule score and scoring methodology strictly.
          6. Preserves original finding IDs and finding count (never silently drops findings).
          7. Validates against ATSAnalyzeResponse schema.
          8. Returns ATSAnalyzeResponse(summary=..., findings=...).
        """
        if isinstance(request, dict):
            request = ATSAnalyzeRequest.model_validate(request)
        elif not isinstance(request, ATSAnalyzeRequest):
            raise ValueError("request must be an instance of ATSAnalyzeRequest.")

        # 1. Build prompt using existing prompt builder
        prompt = build_ats_analysis_prompt(request)

        # 2. Invoke LLM provider
        raw_output = self._invoke_provider(prompt)

        # 3. Parse JSON safely
        data = self._parse_provider_output(raw_output)

        # 4. Extract and validate executive summary
        summary = str(data.get("summary", "")).strip()
        if not summary:
            raise LLMParseError(
                "ATS refinement response did not contain an executive summary.",
                raw_content=str(raw_output),
                status_code=502,
            )

        # 5. Preserve deterministic rule findings & original IDs:
        # Every original finding ID in request.rule_findings must be present.
        orig_findings = request.rule_findings or []
        raw_findings = data.get("findings", [])
        if not isinstance(raw_findings, list):
            raw_findings = []

        llm_findings_by_id: Dict[str, Dict[str, Any]] = {}
        for item in raw_findings:
            if isinstance(item, dict) and item.get("id"):
                llm_findings_by_id[str(item["id"]).strip()] = item

        refined_findings: List[RuleFinding] = []
        for idx, orig_f in enumerate(orig_findings):
            # Attempt exact ID match first, then positional fallback
            llm_item = llm_findings_by_id.get(orig_f.id)
            if not llm_item and idx < len(raw_findings) and isinstance(raw_findings[idx], dict):
                llm_item = raw_findings[idx]

            if llm_item:
                raw_sev = llm_item.get("severity")
                severity = orig_f.severity
                if raw_sev:
                    try:
                        severity = ATSFindingSeverity(str(raw_sev).strip().lower())
                    except ValueError:
                        severity = orig_f.severity

                refined_findings.append(
                    RuleFinding(
                        id=orig_f.id,  # STRICTLY PRESERVE ORIGINAL ID
                        category=str(llm_item.get("category") or orig_f.category).strip(),
                        severity=severity,
                        title=str(llm_item.get("title") or orig_f.title).strip(),
                        description=str(llm_item.get("description") or orig_f.description).strip(),
                        recommendation=str(llm_item.get("recommendation") or orig_f.recommendation or "").strip() or None,
                    )
                )
            else:
                # LLM omitted or dropped finding: preserve original finding so findings are never lost
                refined_findings.append(orig_f)

        # 6. Validate against ATSAnalyzeResponse
        try:
            response = ATSAnalyzeResponse(
                summary=summary,
                findings=refined_findings,
            )
        except ValidationError as val_err:
            raise LLMParseError(
                f"ATS analysis output failed schema validation: {str(val_err)}",
                raw_content=str(raw_output),
                status_code=502,
            )

        return response

    # Aliases for flexibility
    refine_ats = analyze_ats
    refine_ats_analysis = analyze_ats
    analyze_ats_feedback = analyze_ats


# ---------------------------------------------------------------------------
# Singleton Factory
# ---------------------------------------------------------------------------

_career_service: Optional[CareerService] = None


def get_career_service(provider=None) -> CareerService:
    """
    Factory returning singleton CareerService or new instance if custom provider is supplied.
    """
    global _career_service
    if provider is not None:
        return CareerService(provider=provider)

    from app.core.config import settings
    from app.services.llm_provider import MockLLMProvider

    # If the configured provider mode changed (e.g. in tests switching to mock), refresh singleton
    if _career_service is not None:
        is_mock_configured = settings.LLM_PROVIDER.lower() == "mock" or not bool(settings.GROQ_API_KEY)
        is_mock_instance = isinstance(_career_service._provider, MockLLMProvider)
        if is_mock_configured != is_mock_instance:
            _career_service = None

    if _career_service is None:
        _career_service = CareerService()
    return _career_service
