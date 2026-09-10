# UniOS-KIE-Core

KIE Core and orchestration service for **UniOS.ai**.

KIE (Knowledge, Intelligence & Execution) is responsible for
understanding learner requests, building execution plans,
selecting agents, routing model capabilities, invoking approved
tools, and returning structured intelligence responses.

---

## 🎯 Purpose

KIE Core acts as the intelligence and orchestration layer
between the UniOS platform and AI capabilities.

The current implementation focuses on:

- Learner identity resolution
- Learner context assembly
- Intent recognition
- Execution planning
- Agent orchestration
- Tool execution
- Model routing
- Execution tracing
- Structured API responses

---

## 🏗️ Architecture

```text
UniOS Backend
      |
      | normalized learner profile/context
      v
  KIE API
      |
      v
Identity Engine
      |
      v
Context Engine
      |
      v
Intent Engine
      |
      v
Model Router
      |
      v
Planning Engine
      |
      v
Agent Registry
      |
      v
Execution Engine
      |
      +------> Tool Engine
      |
      v
Structured KIE Response
