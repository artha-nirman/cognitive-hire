# Development Guide

This guide provides instructions for setting up your development environment and contributing to the Cognitive Hire platform.

<!-- In development-guide.md -->
> **Prerequisites**: Make sure you've completed the [Environment Setup](environment-setup.md) before starting development.


## Environment Setup

1. **Prerequisites Installation**
   - Follow the [Environment Setup Guide](./environment-setup.md) to install all required tools and dependencies
   - Make sure you have Node.js, npm, Python, and Docker installed
   - Complete the authentication setup for Azure services

2. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/cognitive-hire.git
   cd cognitive-hire
   ```

3. **Install Dependencies**

   Backend services:
   ```bash
   # For each service (e.g., recruitment-service)
   cd backend/recruitment-service
   pip install -r requirements.txt
   ```

   Frontend application:
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Environment Variables**
   - Use the script to fetch secrets from Azure Key Vault:
     ```bash
     python scripts/setup-env.py --service recruitment
     ```
   - Or manually create `.env` files as described in the [Environment Setup Guide](./environment-setup.md)

## Running Services Locally

### Backend Services

1. **Run with Python directly**
   ```bash
   cd backend/recruitment-service
   uvicorn src.main:app --reload
   ```

2. **Run with Docker**
   ```bash
   cd backend/recruitment-service
   docker-compose up
   ```

### Frontend Application

1. **Development mode**
   ```bash
   cd frontend
   npm run dev
   ```

2. **Production build**
   ```bash
   cd frontend
   npm run build
   npm start
   ```

## Testing

### Backend Tests

```bash
cd backend/recruitment-service
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Code Contribution Guidelines

1. **Branch naming**
   - Feature branches: `feature/short-description`
   - Bug fixes: `fix/issue-description`
   - Refactoring: `refactor/component-name`

2. **Commit messages**
   - Follow the conventional commits format
   - Example: `feat(job): add multi-channel publishing support`

3. **Pull Requests**
   - Include a clear description of the changes
   - Link to related issues or tasks
   - Ensure all tests pass before requesting review

4. **Code Style**
   - Backend: Follow PEP 8 and use Black formatter
   - Frontend: Follow ESLint and Prettier configurations
   - Run linters before committing: `pre-commit run --all-files`

## Working with APIs

- REST API documentation: http://localhost:8000/docs
- WebSocket API documentation: http://localhost:8000/async-docs
- Use the API clients in `frontend/src/lib/api-client.ts` for frontend integration

## Documentation

- Update documentation when changing functionality
- Document APIs using OpenAPI and AsyncAPI specifications
- Include examples in documentation when possible

## Troubleshooting

### Common Issues

1. **Environment variable issues**
   - Check that all variables in `.env.example` are set in your `.env` file
   - Verify Azure AD B2C configuration for authentication

2. **Frontend build failures**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check TypeScript compiler errors: `npm run type-check`

3. **Backend service errors**
   - Verify database connection: `python -m src.utils.check_db_connection`
   - Check service logs: `docker-compose logs -f recruitment-service`
