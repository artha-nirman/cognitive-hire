# Cognitive Hire API Reference

This document provides an overview of the Cognitive Hire API ecosystem and serves as a guide to the detailed API documentation maintained alongside each service.

## API Architecture

Cognitive Hire follows a domain-driven design with multiple microservices, each exposing its own API:

```mermaid
graph TD
    Client[Client Applications] --> Gateway[API Gateway]
    Gateway --> RecruitmentAPI[Recruitment Service API]
    Gateway --> CandidateAPI[Candidate Service API]
    Gateway --> WorkflowAPI[Workflow Service API]
    Gateway --> SchedulingAPI[Scheduling Service API]
    Gateway --> CommunicationsAPI[Communications Service API]
```

Each service maintains its own OpenAPI and AsyncAPI specifications in its `/api` directory.

## Service API Documentation

| Service | Domain | API Spec Location | Main Capabilities |
|---------|--------|-------------------|------------------|
| Recruitment | Employer, Job, Publishing | [Recruitment OpenAPI](../backend/recruitment-service/api/openapi.yaml) | Employer management, job postings, multi-channel publishing |
| Candidate | Candidate profiles, Applications | [Candidate OpenAPI](../backend/candidate-service/api/openapi.yaml) | Candidate profiles, resume parsing, application tracking |
| Workflow | Pipeline, Interview | [Workflow OpenAPI](../backend/workflow-service/api/openapi.yaml) | Recruitment stages, workflows, approvals |
| Scheduling | Calendar, Availability | [Scheduling OpenAPI](../backend/scheduling-service/api/openapi.yaml) | Interview scheduling, calendar integration |
| Screening | Skills matching, Assessments | [Screening OpenAPI](../backend/screening-service/api/openapi.yaml) | Resume screening, skills matching, assessments |

## Authentication

All API requests require authentication through JWT tokens. 

```http
GET /api/jobs HTTP/1.1
Host: api.cognitivehire.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsIn...
X-Tenant-ID: 12345678-90ab-cdef-1234-567890abcdef
```

Detailed authentication documentation is available in the [Security Framework Guide](../docs/security-guide.md).

## Real-time APIs

In addition to REST APIs, Cognitive Hire provides WebSocket endpoints for real-time updates:

| Service | WebSocket API Spec | Use Cases |
|---------|-------------------|-----------|
| Recruitment | [Recruitment AsyncAPI](../backend/recruitment-service/api/asyncapi.yaml) | Job posting status updates |
| Workflow | [Workflow AsyncAPI](../backend/workflow-service/api/asyncapi.yaml) | Pipeline stage transitions, interview feedback |
| Screening | [Screening AsyncAPI](../backend/screening-service/api/asyncapi.yaml) | Real-time candidate matching results |

## Response Formats

All REST APIs return JSON responses with a consistent structure:

```json
{
  "data": { /* Response data */ },
  "meta": { 
    "page": 1,
    "per_page": 25,
    "total": 100
  },
  "errors": [] // Present only when there are errors
}
```

## Error Handling

Errors follow a consistent format across all APIs:

```json
{
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Invalid input data",
      "details": { /* Error-specific details */ }
    }
  ]
}
```

Standard HTTP status codes are used across all services.

## API Versioning

APIs are versioned through URL paths: `/api/v1/resource`

We maintain backward compatibility within a major version. Breaking changes require a new major version.

## Rate Limiting

API rate limits depend on subscription tier:

| Plan | Rate Limit | Burst Limit |
|------|------------|-------------|
| Basic | 60 req/min | 100 req/min |
| Pro | 300 req/min | 500 req/min |
| Enterprise | Custom | Custom |

Rate limit headers are included in all responses:

