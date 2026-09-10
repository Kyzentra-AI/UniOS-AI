# UniOS → KIE Integration Contract

## Purpose

This document defines the integration contract between the
UniOS Backend and KIE Core for learner identity, context,
intent, planning, orchestration, tools, and model routing.

UniOS Backend owns persistent learner profile and onboarding state.

KIE consumes normalized learner information and uses it
during intelligence and orchestration.

---

## Endpoint

POST `/kie/execute`

---

## Identity

UniOS provides:

```json
{
  "user_id": "unios-user-001",
  "session_id": "unios-session-001",
  "role": "student"
}