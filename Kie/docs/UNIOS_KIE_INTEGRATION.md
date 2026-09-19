# UniOS ↔ KIE Integration Contract

## 1. Purpose

This document defines the integration contract between the UniOS Backend and
KIE Core.

KIE is responsible for intelligence and orchestration.

Backend is responsible for persistent application data, authentication,
storage, and external system integration.

---

## 2. KIE Service Endpoints

### Health Check

```http
GET /health