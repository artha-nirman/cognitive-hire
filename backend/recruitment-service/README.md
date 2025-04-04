# Recruitment Service

This service implements the following domains from the Cognitive Hire architecture:
- Employer Domain: Organization and team management
- Job Domain: Job definition and management
- Publishing Domain: Multi-channel job distribution
- Screening Domain: Candidate evaluation
- Sourcing Domain: Candidate acquisition

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run locally: `uvicorn src.main:app --reload`
4. With Docker: `docker-compose up`

## Architecture

The service follows a domain-driven design approach with:
- FastAPI for REST and WebSocket APIs
- PostgreSQL for relational data
- Event-driven communication with other services
- Domain-specific business logic isolation

## Development Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) style guide
- Add tests for new features
- Update API specifications when changing endpoints
- Run linting before commits: `pre-commit run --all-files`

## Testing

Run tests with pytest:
```
pytest
```

## API Documentation

When running locally, access API documentation at:
- REST API: http://localhost:8000/docs
- WebSocket API: http://localhost:8000/async-docs
