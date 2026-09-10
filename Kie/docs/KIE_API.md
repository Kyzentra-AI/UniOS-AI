# KIE Core API

## Overview

KIE Core is the intelligence and orchestration service for UniOS.ai.

The KIE execution flow currently performs:

1. Identity resolution
2. Context resolution
3. Intent recognition
4. Planning
5. Agent selection
6. Execution
7. Structured response generation

---

## Health Check

### GET `/health`

Returns the health status of the KIE service.

Example response:

```json
{
  "status": "ok",
  "service": "kie-core"
}