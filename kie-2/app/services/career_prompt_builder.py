"""
UniOS Sprint 7 — Career Prompt Builders (AI/ML-2 KIE)
Tasks:
  - BE-S7-01 & BE-S7-04: AI Resume Generation Prompt Builder
  - ATS Resume Checker Prompt Builder (Qualitative Refinement)

ARCHITECTURAL BOUNDARIES & INVARIANTS:
  - Follows existing project prompt builder conventions (build_prompt_builder.py, onboarding_prompt_builder.py).
  - Strictly grounded: Never invents degrees, institutions, employers, projects, or metrics.
  - Zero database access, ORM dependencies, or external API calls.
  - Enforces JSON output schemas matching ResumeDraft and ATSAnalyzeResponse.
"""

from typing import List, Optional
import json

from app.schemas.career import (
    ATSAnalyzeRequest,
    CareerContext,
    DocumentMetadata,
    ResumeAchievement,
    ResumeContact,
    ResumeDraft,
    ResumeEducation,
    ResumeExperience,
    ResumeGenerateRequest,
    ResumePreferences,
    ResumeProject,
    ResumeTone,
    RuleFinding,
    RuleScore,
)


# ---------------------------------------------------------------------------
# Formatting Helpers for Resume Generation
# ---------------------------------------------------------------------------

def _format_contact(contact: Optional[ResumeContact]) -> str:
    if not contact:
        return "  [No contact information provided. Do NOT fabricate any contact details.]"

    lines = []
    if contact.full_name:
        lines.append(f"  - Full Name: {contact.full_name}")
    if contact.email:
        lines.append(f"  - Email: {contact.email}")
    if contact.phone:
        lines.append(f"  - Phone: {contact.phone}")
    if contact.location:
        lines.append(f"  - Location: {contact.location}")
    if contact.linkedin_url:
        lines.append(f"  - LinkedIn: {contact.linkedin_url}")
    if contact.github_url:
        lines.append(f"  - GitHub: {contact.github_url}")
    if contact.portfolio_url:
        lines.append(f"  - Portfolio: {contact.portfolio_url}")

    # Note unprovided contact details
    unprovided = []
    if not contact.phone:
        unprovided.append("Phone")
    if not contact.email:
        unprovided.append("Email")
    if not contact.linkedin_url:
        unprovided.append("LinkedIn")
    if not contact.github_url:
        unprovided.append("GitHub")
    if not contact.portfolio_url:
        unprovided.append("Portfolio")
    if not contact.location:
        unprovided.append("Location")

    if unprovided:
        lines.append(f"  - Missing/Unprovided: {', '.join(unprovided)} (Do NOT fabricate or invent; leave as null)")

    if not lines:
        return "  [No contact details provided. Do NOT fabricate contact details.]"
    return "\n".join(lines)


def _format_education(education: List[ResumeEducation]) -> str:
    if not education:
        return "  [No education entries provided. Do NOT invent new degrees or institutions.]"

    entries = []
    for idx, edu in enumerate(education, start=1):
        field_str = f" in {edu.field_of_study}" if edu.field_of_study else ""
        deg_str = f"{edu.degree}{field_str}" if edu.degree else "Degree unspecified"
        dates = []
        if edu.start_date:
            dates.append(edu.start_date)
        if edu.end_date:
            dates.append(edu.end_date)
        dates_str = f" ({' - '.join(dates)})" if dates else ""
        grade_str = f" [Grade: {edu.grade}]" if edu.grade else ""
        id_str = f" (ID: {edu.id})" if edu.id else ""
        entries.append(f"  {idx}. {edu.institution} — {deg_str}{dates_str}{grade_str}{id_str}")
    return "\n".join(entries)


def _format_experience(experience: List[ResumeExperience]) -> str:
    if not experience:
        return "  [No work experience provided. Do NOT invent companies or roles.]"

    entries = []
    for idx, exp in enumerate(experience, start=1):
        role_str = exp.role if exp.role else "Role unspecified"
        loc_str = f" ({exp.location})" if exp.location else ""
        dates = []
        if exp.start_date:
            dates.append(exp.start_date)
        dates.append("Present" if exp.is_current else (exp.end_date or ""))
        dates_clean = " - ".join([d for d in dates if d])
        dates_str = f" [{dates_clean}]" if dates_clean else ""
        id_str = f" (ID: {exp.id})" if exp.id else ""
        desc_str = f"\n     Description: {exp.description}" if exp.description else ""
        entries.append(f"  {idx}. {exp.company} — {role_str}{loc_str}{dates_str}{id_str}{desc_str}")
    return "\n".join(entries)


def _format_projects(projects: List[ResumeProject]) -> str:
    if not projects:
        return "  [No projects provided. Do NOT invent new projects.]"

    entries = []
    for idx, proj in enumerate(projects, start=1):
        tech_str = f" [Tech: {', '.join(proj.technologies)}]" if proj.technologies else ""
        url_str = f" (URL: {proj.project_url})" if proj.project_url else ""
        id_str = f" (ID: {proj.id})" if proj.id else ""
        desc_str = f"\n     Description: {proj.description}" if proj.description else ""
        entries.append(f"  {idx}. {proj.name}{tech_str}{url_str}{id_str}{desc_str}")
    return "\n".join(entries)


def _format_achievements(achievements: List[ResumeAchievement]) -> str:
    if not achievements:
        return "  [No achievements provided. Do NOT invent phantom certifications or awards.]"

    entries = []
    for idx, ach in enumerate(achievements, start=1):
        date_str = f" ({ach.date})" if ach.date else ""
        id_str = f" (ID: {ach.id})" if ach.id else ""
        desc_str = f"\n     Detail: {ach.description}" if ach.description else ""
        entries.append(f"  {idx}. {ach.title}{date_str}{id_str}{desc_str}")
    return "\n".join(entries)


def _format_career_context(career_context: Optional[CareerContext]) -> str:
    if not career_context:
        return "  [No external career context supplied.]"

    lines = []
    if career_context.learner:
        l = career_context.learner
        if l.primary_goal:
            lines.append(f"  - Learner Primary Goal: {l.primary_goal}")
        if l.skills:
            lines.append(f"  - Verified Learner Skills: {', '.join(l.skills)}")
        if l.experience:
            lines.append(f"  - Learner Background: {l.experience}")

    if career_context.education:
        e = career_context.education
        edu_parts = []
        if e.university:
            edu_parts.append(f"University: {e.university}")
        if e.degree_program:
            edu_parts.append(f"Program: {e.degree_program}")
        if e.domain:
            edu_parts.append(f"Domain: {e.domain}")
        if e.academic_status:
            edu_parts.append(f"Status: {e.academic_status}")
        if edu_parts:
            lines.append(f"  - Verified Education: {', '.join(edu_parts)}")

    if career_context.career_readiness:
        cr = career_context.career_readiness
        if cr.projects:
            lines.append("  - Verified Build Projects:")
            for p in cr.projects:
                p_skills = f" (Skills: {', '.join(p.skills)})" if p.skills else ""
                lines.append(f"    * {p.title}{p_skills}: {p.description or ''}")

        if cr.evidence:
            lines.append("  - Quantified Build Evidence:")
            for ev in cr.evidence:
                ev_skills = f" [{', '.join(ev.skills)}]" if ev.skills else ""
                lines.append(f"    * {ev.title}{ev_skills}: {ev.description or ''}")

        if cr.mastery:
            lines.append("  - Validated Topic Mastery:")
            for m in cr.mastery:
                status_str = f" ({m.status})" if m.status else ""
                lines.append(f"    * {m.topic}: {m.mastery_score:.0%}{status_str}")

    if not lines:
        return "  [Career context provided contains no additional evidence.]"
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Formatting Helpers for ATS Analysis
# ---------------------------------------------------------------------------

def _format_rule_findings(findings: List[RuleFinding]) -> str:
    if not findings:
        return "  [No rule findings reported by deterministic engine.]"

    lines = []
    for idx, f in enumerate(findings, start=1):
        lines.append(
            f"  {idx}. Finding ID: {f.id}\n"
            f"     Category: {f.category} | Severity: {f.severity.value}\n"
            f"     Title: {f.title}\n"
            f"     Description: {f.description}\n"
            f"     Initial Recommendation: {f.recommendation or 'None provided.'}"
        )
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# 1. Resume Generation Prompt Builder
# ---------------------------------------------------------------------------

def build_resume_generation_prompt(
    request: Optional[ResumeGenerateRequest] = None,
    *,
    content: Optional[ResumeDraft] = None,
    preferences: Optional[ResumePreferences] = None,
    career_context: Optional[CareerContext] = None,
    title: Optional[str] = None,
) -> str:
    """
    Constructs a strictly grounded prompt for LLM resume tailoring & synthesis.
    Adheres to Section 3 and Section 5 of launch_aiml_integration_guide.md.

    Enforces:
      - Anti-hallucination whitelist: Allowed institutions, companies, project titles.
      - Tone and length constraints (concise: < 20 words per bullet).
      - Target role skill prioritization.
      - Exact JSON structure matching ResumeDraft.
    """
    if request:
        content = request.content
        preferences = request.preferences
        career_context = request.career_context
        title = request.title

    if not content:
        raise ValueError("ResumeDraft content is required to build resume generation prompt.")

    target_role = (preferences.target_role if preferences and preferences.target_role else (title or "Software Professional")).strip()
    tone = preferences.tone if preferences and preferences.tone else ResumeTone.PROFESSIONAL

    # Determine grounding whitelist from content and career context
    allowed_institutions = set()
    for e in content.education:
        if e.institution:
            allowed_institutions.add(e.institution.strip())
    if career_context and career_context.education and career_context.education.university:
        allowed_institutions.add(career_context.education.university.strip())

    allowed_companies = set()
    for exp in content.experience:
        if exp.company:
            allowed_companies.add(exp.company.strip())

    allowed_projects = set()
    for p in content.projects:
        if p.name:
            allowed_projects.add(p.name.strip())
    if career_context and career_context.career_readiness:
        for cr_p in career_context.career_readiness.projects:
            if cr_p.title:
                allowed_projects.add(cr_p.title.strip())

    inst_str = ", ".join(f'"{i}"' for i in sorted(allowed_institutions)) if allowed_institutions else "[None provided]"
    comp_str = ", ".join(f'"{c}"' for c in sorted(allowed_companies)) if allowed_companies else "[None provided]"
    proj_str = ", ".join(f'"{p}"' for p in sorted(allowed_projects)) if allowed_projects else "[None provided]"

    tone_instruction = (
        "- Tone: CONCISE. Keep every bullet point strictly under 20 words. Lead directly with vigorous action verbs."
        if tone == ResumeTone.CONCISE
        else "- Tone: PROFESSIONAL. Use executive, outcomes-focused engineering terminology and Google XYZ framing ('Accomplished [X], measured by [Y], by doing [Z]'). Keep bullet points under 25 words."
    )

    return f"""You are the UniOS Career Intelligence Engine (AI/ML-2 KIE).
Synthesize and tailor an elevated, professionally grounded resume draft based strictly on the learner's current draft and verified career evidence.

CRITICAL GROUNDING & ANTI-HALLUCINATION INVARIANTS (NON-NEGOTIABLE):
1. NEVER INVENT CREDENTIALS OR METRICS:
   - Do NOT invent degrees, certificates, GPAs, dates, organizations, or metrics.
   - Do NOT invent companies or employers. Allowed companies: {comp_str}.
   - Do NOT invent schools or universities. Allowed institutions: {inst_str}.
   - Do NOT invent project names. Allowed projects: {proj_str}.
   - If contact details (phone, LinkedIn, GitHub, portfolio) are missing, keep them null. NEVER invent mock or sample contact information.
2. ELEVATE, DO NOT FABRICATE:
   - Strengthen existing bullet points using action verbs (e.g., 'Architected', 'Engineered', 'Optimized', 'Containerized', 'Spearheaded') and quantified data from verified evidence.
   - Maintain the learner's authentic career narrative while tailoring it for '{target_role}'.
3. ROLE & PREFERENCE ALIGNMENT:
   - Target Role: '{target_role}'. Prioritize skills, frameworks, and architecture patterns relevant to this role.
   {tone_instruction}
4. PRESERVE ORIGINAL IDS:
   - For all education, experience, project, and achievement entries that provide an 'id', preserve the exact 'id' in your output.

BASE RESUME DRAFT (USER INPUT):
- Resume Title: {title or 'Unspecified'}
- Contact Information:
{_format_contact(content.contact)}
- Current Headline: {content.headline or '[None provided]'}
- Current Summary: {content.summary or '[None provided]'}
- Core Skills: {', '.join(content.skills) if content.skills else '[None declared]'}
- Education Entries:
{_format_education(content.education)}
- Work Experience Entries:
{_format_experience(content.experience)}
- Projects:
{_format_projects(content.projects)}
- Achievements & Certifications:
{_format_achievements(content.achievements)}

VERIFIED CAREER CONTEXT (DATABASE GROUNDING EVIDENCE):
{_format_career_context(career_context)}

OUTPUT FORMAT REQUIREMENTS:
Output strictly valid JSON matching the following structure. Do NOT include markdown outside of the JSON block or conversational commentary:
{{
  "contact": {{
    "fullName": "{content.contact.full_name if content.contact and content.contact.full_name else ''}",
    "email": "{content.contact.email if content.contact and content.contact.email else ''}",
    "phone": {json.dumps(content.contact.phone if content.contact else None)},
    "location": {json.dumps(content.contact.location if content.contact else None)},
    "linkedInUrl": {json.dumps(content.contact.linkedin_url if content.contact else None)},
    "githubUrl": {json.dumps(content.contact.github_url if content.contact else None)},
    "portfolioUrl": {json.dumps(content.contact.portfolio_url if content.contact else None)}
  }},
  "headline": "<Synthesized impactful headline targeting {target_role}>",
  "summary": "<2-4 sentences executive summary grounded strictly in authentic experience and verified mastery>",
  "skills": ["<prioritized_skill_1>", "<prioritized_skill_2>"],
  "education": [
    {{
      "id": "<preserve_id>",
      "institution": "<allowed_institution>",
      "degree": "<degree>",
      "fieldOfStudy": "<field>",
      "startDate": "<date>",
      "endDate": "<date>",
      "grade": "<grade_or_null>"
    }}
  ],
  "experience": [
    {{
      "id": "<preserve_id>",
      "company": "<allowed_company>",
      "role": "<elevated_role>",
      "location": "<location>",
      "startDate": "<date>",
      "endDate": "<date>",
      "isCurrent": false,
      "description": "<Bullet points starting with action verbs, incorporating verified evidence metrics, under 20 words each>"
    }}
  ],
  "projects": [
    {{
      "id": "<preserve_id>",
      "name": "<allowed_project_name>",
      "description": "<Concise outcome-focused project description incorporating evidence>",
      "technologies": ["<tech1>", "<tech2>"],
      "projectUrl": "<url>",
      "startDate": "<date>",
      "endDate": "<date>"
    }}
  ],
  "achievements": [
    {{
      "id": "<preserve_id>",
      "title": "<title>",
      "description": "<description>",
      "date": "<date>"
    }}
  ]
}}
"""


# ---------------------------------------------------------------------------
# 2. ATS Analysis Prompt Builder
# ---------------------------------------------------------------------------

def build_ats_analysis_prompt(
    request: Optional[ATSAnalyzeRequest] = None,
    *,
    extracted_text: Optional[str] = None,
    rule_score: Optional[RuleScore] = None,
    rule_findings: Optional[List[RuleFinding]] = None,
    document: Optional[DocumentMetadata] = None,
) -> str:
    """
    Constructs a prompt for ATS resume analysis qualitative refinement.
    Adheres to Section 4 of launch_aiml_integration_guide.md.

    Enforces:
      - 2–4 sentences executive summary assessing strengths and ATS readiness.
      - Preservation of exact finding IDs from deterministic rule findings.
      - Actionable, specific recommendations (e.g. Google XYZ formula, metric density).
      - Strict prohibition on altering the deterministic rule score.
      - Exact JSON structure matching ATSAnalyzeResponse.
    """
    if request:
        extracted_text = request.extracted_text
        rule_score = request.rule_score
        rule_findings = request.rule_findings
        document = request.document

    if extracted_text is None:
        raise ValueError("extracted_text is required to build ATS analysis prompt.")
    if rule_score is None:
        raise ValueError("rule_score is required to build ATS analysis prompt.")
    if rule_findings is None:
        rule_findings = []

    # Safeguard token budget: truncate extracted text if excessively long (> 12,000 chars)
    max_text_chars = 12000
    if len(extracted_text) > max_text_chars:
        text_for_prompt = extracted_text[:max_text_chars] + "\n... [Remaining extracted text truncated for length] ..."
    else:
        text_for_prompt = extracted_text

    doc_name = document.file_name if document else "Uploaded Resume Document"
    doc_type = document.file_type.value if document else "unspecified"
    pages = str(document.page_count) if (document and document.page_count is not None) else "unspecified"

    return f"""You are the UniOS ATS Intelligence Engine (AI/ML-2 KIE).
Review the candidate's extracted resume text alongside deterministic rule-based checks. Synthesize a comprehensive qualitative executive summary and enrich each rule finding with specific, actionable feedback.

CRITICAL EVALUATION & BOUNDARY RULES:
1. PRESERVE DETERMINISTIC SCORE BOUNDARY:
   - The deterministic ATS score is {rule_score.value:.1f} / {rule_score.max_value:.1f} (Methodology: {rule_score.methodology}).
   - You MUST NOT calculate a new numerical score or claim that your qualitative analysis changes the deterministic score.
2. EXECUTIVE SUMMARY:
   - Produce a cohesive executive summary of exactly 2 to 4 sentences.
   - Summarize the candidate's core strengths (education, technical foundations) and primary ATS filter liabilities (e.g., missing metrics, passive phrasing, missing contact/links).
3. ENRICH RULE FINDINGS WITH HIGH SPECIFICITY:
   - You MUST keep the exact 'id' for each finding from the input rule findings.
   - Refine the 'title' to be assertive and professional.
   - Expand the 'description' to explain clearly why ATS parsers or recruiters flag this issue.
   - Provide concrete, actionable 'recommendation' (e.g., cite the Google XYZ formula: 'Accomplished [X], as measured by [Y], by doing [Z]', recommend strong verbs, specify where to add links).
   - Assign appropriate severity ('info', 'suggestion', 'warning', 'critical'). Upgrade to 'critical' if the flaw severely jeopardizes ATS screening.
4. GROUNDING:
   - Base all critique strictly on the extracted text below. Do not fabricate issues not substantiated by the document.

DOCUMENT METADATA:
- File Name: {doc_name}
- File Format: {doc_type}
- Pages: {pages}

DETERMINISTIC RULE SCORE:
- Score: {rule_score.value:.1f} / {rule_score.max_value:.1f} ({rule_score.methodology} v{rule_score.methodology_version or '1.0'})

INITIAL RULE FINDINGS FROM ENGINE:
{_format_rule_findings(rule_findings)}

EXTRACTED RESUME TEXT:
\"\"\"
{text_for_prompt}
\"\"\"

OUTPUT FORMAT REQUIREMENTS:
Output strictly valid JSON matching the following structure. Do NOT include markdown outside of the JSON block or conversational commentary:
{{
  "summary": "<2-4 sentences executive summary assessing candidate's ATS strengths and key liabilities>",
  "findings": [
    {{
      "id": "<exact_original_finding_id>",
      "category": "<category>",
      "severity": "info" | "suggestion" | "warning" | "critical",
      "title": "<Refined assertive title>",
      "description": "<Detailed explanation of ATS parsing or recruiter screening impact>",
      "recommendation": "<Specific, actionable advice (e.g., XYZ formula, concrete examples)>"
    }}
  ]
}}
"""
