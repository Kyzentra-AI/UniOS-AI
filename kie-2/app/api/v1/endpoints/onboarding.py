from fastapi import APIRouter, HTTPException, status
from app.schemas import (
    OnboardingInputProfile,
    LearnerIntelligenceReport,
    LearnerProfileValidationResult,
    LearnerStage,
)
from app.services import (
    build_onboarding_intelligence_prompt,
    get_llm_provider,
    LLMProviderError,
    LLMParseError,
)

router = APIRouter()


@router.post(
    "/validate-profile",
    response_model=LearnerProfileValidationResult,
    status_code=status.HTTP_200_OK,
    summary="Validate Learner Onboarding Profile (Preflight)",
    description=(
        "Performs lightweight validation and normalization of onboarding profile inputs "
        "without invoking the LLM provider. Checks data completeness, skill baseline counts, "
        "and provides heuristic readiness indicators."
    ),
    responses={
        200: {
            "description": "Validation completed successfully.",
            "model": LearnerProfileValidationResult,
        },
        422: {
            "description": "Unprocessable Entity - Schema validation error.",
        },
    },
)
def validate_onboarding_profile(
    profile: OnboardingInputProfile,
) -> LearnerProfileValidationResult:
    """Preflight validation endpoint: validates onboarding data and returns diagnostic feedback without calling LLM."""
    issues = []
    recommendations = []

    # 1. Skill baseline checks
    skills_count = len(profile.declared_skills)
    if skills_count == 0:
        issues.append("No technical skills declared. Scaffolding recommendations will use default entry-level assumptions.")
        recommendations.append("Declare at least 2-3 baseline skills or tools to calibrate prerequisite depth.")
    elif skills_count < 3:
        recommendations.append("Consider declaring secondary tools (e.g. Git, Docker, SQL) for more precise role gap analysis.")

    # 2. Weekly study hours calibration
    weekly_hours = profile.get_effective_weekly_hours()
    if weekly_hours is not None:
        if weekly_hours < 5:
            issues.append("Weekly commitment is under 5 hours. May prolong milestone progression.")
            recommendations.append("Dedicate at least 6-10 hours weekly to ensure consistent momentum.")
        elif weekly_hours >= 40:
            recommendations.append("High study volume detected (40+ h/week). Ensure pacing includes regular rest to avoid burnout.")
    else:
        recommendations.append("Specify estimated weekly study hours to enable accurate milestone timeline projections.")

    # 3. Target role and motivation
    if not profile.motivation_statement or len(profile.motivation_statement.strip()) < 10:
        recommendations.append("Add a detailed motivation statement to enable personalized engagement hooks.")

    # 4. Stage-specific recommendations
    if profile.stage == LearnerStage.GRADUATE and not profile.prior_projects_summary:
        recommendations.append("Graduate transition profiles benefit strongly from prior coursework or project summaries.")

    # Heuristic indicator calculation
    if skills_count >= 4:
        avg_rating = sum(s.self_rating for s in profile.declared_skills) / skills_count
        if avg_rating >= 3.5:
            readiness_indicator = "accelerated_curriculum"
        elif avg_rating >= 2.5:
            readiness_indicator = "standard_curriculum"
        else:
            readiness_indicator = "scaffolded_curriculum"
    elif skills_count >= 1:
        readiness_indicator = "standard_curriculum"
    else:
        readiness_indicator = "foundational_scaffolding"

    return LearnerProfileValidationResult(
        is_valid=True,
        learner_id=profile.learner_id,
        stage=profile.stage,
        target_role=profile.get_effective_target_role(),
        issues=issues,
        recommendations=recommendations,
        declared_skills_count=skills_count,
        estimated_readiness_indicator=readiness_indicator,
    )


@router.post(
    "/analyze",
    response_model=LearnerIntelligenceReport,
    status_code=status.HTTP_200_OK,
    summary="Analyze Learner Onboarding Profile (Sprint-2)",
    description=(
        "Ingests normalized learner onboarding data from UniOS Backend / KIE, "
        "evaluates 6 core intelligence dimensions (skill, knowledge, learning style, career, "
        "motivation, readiness), and returns a structured Learner Intelligence Report."
    ),
    responses={
        200: {
            "description": "Successful generation of structured Learner Intelligence Report.",
            "model": LearnerIntelligenceReport,
        },
        422: {
            "description": "Validation error: Malformed or invalid onboarding profile input.",
        },
        502: {
            "description": "Bad Gateway: LLM provider unavailable or response could not be validated.",
        },
        429: {
            "description": "Too Many Requests: LLM provider rate limit exceeded.",
        },
    },
)
@router.post(
    "/learner-intelligence",
    response_model=LearnerIntelligenceReport,
    status_code=status.HTTP_200_OK,
    summary="Analyze Learner Intelligence (Backward-Compatible Alias)",
    description="Backward-compatible alias endpoint for analyzing learner onboarding data.",
    include_in_schema=True,
    responses={
        200: {
            "description": "Successful generation of structured Learner Intelligence Report.",
            "model": LearnerIntelligenceReport,
        },
        422: {"description": "Validation error."},
        502: {"description": "Provider error."},
    },
)
def analyze_onboarding_profile(
    profile: OnboardingInputProfile,
) -> LearnerIntelligenceReport:
    """AI/ML-2 capability interface: Produces multi-dimensional Learner Intelligence from onboarding profile.
    Stateless, secure, and privacy-preserving.
    """
    stage_str = profile.stage.value if profile.stage else "unspecified"
    print(
        f">>> [API /api/v1/onboarding] Processing request: "
        f"learner='{profile.learner_id}', stage='{stage_str}', "
        f"role='{profile.get_effective_target_role()}', declared_skills={len(profile.declared_skills)}"
    )

    provider = get_llm_provider()

    # 1. Build structured, token-budgeted onboarding prompt
    prompt = build_onboarding_intelligence_prompt(profile)

    # 2. Invoke provider with application-level error handling
    try:
        report = provider.analyze_learner_onboarding(profile=profile, prompt=prompt)
    except LLMProviderError as err:
        raise HTTPException(status_code=err.status_code, detail=err.message)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected internal error during learner intelligence analysis: {str(err)}",
        )

    print(
        f">>> [API /api/v1/onboarding] Analysis complete for '{report.learner_id}' "
        f"(Readiness: {report.readiness.overall_readiness_score:.2f} - {report.readiness.readiness_tier.value})"
    )
    return report
