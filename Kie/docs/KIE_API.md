# KIE Core API Contract

## Overview

The KIE Core API is the orchestration entry point for UniOS.ai.

It receives a task request, processes intent, creates a plan, executes the plan, and returns a structured response.

---

## Endpoint

### POST `/kie/execute`

Processes a KIE request.

---

## Request

Example:

```json
{
  "user_id": "user-001",
  "session_id": "session-001",
  "task": "Explain how binary search works",
  "intent": null,
  "context": {
    "topic": "data structures"
  },
  "tools": [],
  "constraints": {}
}