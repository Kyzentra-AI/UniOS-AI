# KIE Roadmap Response Contract

## Sprint 3 — Roadmap + Memory

This document defines the structured roadmap response returned by
KIE Core for UniOS Backend and Frontend integration.

---

## Endpoint

```http
POST /kie/execute

## Backend Roadmap Persistence Contract

KIE generates a structured roadmap contract after the
Planning Engine creates the learner-aware execution plan.

KIE does not persist the roadmap in a database.

The Backend owns:

- Persistent roadmap storage
- Roadmap retrieval
- Roadmap updates
- Goal persistence
- Mission persistence
- Cross-device synchronization

KIE owns:

- Learner-aware planning
- Milestone generation
- Planning horizon selection
- Agent assignment
- Roadmap contract generation

### Roadmap Contract

The KIE response exposes the generated roadmap through:

`metadata.roadmap_contract`

Example:

```json
{
  "user_id": "student-001",
  "session_id": "session-001",
  "planning_horizon": "weekly",
  "learner_stage": "final-year",
  "career_goal": "Software Engineer",
  "milestones": [
    {
      "milestone_id": "step-1",
      "description": "Review weekly objectives",
      "agent": "tutor-agent",
      "status": "planned"
    }
  ],
  "milestone_count": 1,
  "planning_status": "generated"
}