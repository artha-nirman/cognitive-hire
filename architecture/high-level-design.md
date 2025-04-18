# High Level Architecture

## Origin and Conceptual Foundation

This high-level architecture implements the vision and requirements outlined in the ["Technology Concept"](concept-paper.md) paper. The architectural decisions made here directly map to the conceptual components defined in the concept diagram.

Key concept-to-architecture mappings:
| Concept Component | Architecture Implementation | Rationale |
|------------------|------------------------------|-----------|
| Authentication | Security Framework (§1) | Implements social login, MFA, and security policies |
| Authorization | Security Framework (§1) | Provides role-based and plan-based access control |
| Registration | Candidate Domain (§2) | Handles user and organization registration |
| Workflow | Recruitment Pipeline Domain (§8) | Handles approval flows and candidate tracking |
| Sourcing | Sourcing Domain (§3) | Manages all candidate acquisition channels |
| Screening | Screening Domain (§4) | Handles candidate evaluation and filtering |
| Publishing | Publishing Domain (§7) | Manages job distribution across channels |
| Scheduling | Scheduling Domain (§10) | Handles interview scheduling and calendaring |
| Notifications | Communications Domain (§11) | Manages all system notifications |
| Data | Analytics Domain (§12) | Provides reporting and data insights |
| Payments | Financial Domain (§13) | Handles payment processing and subscription management |
| Activity | Audit Domain (§15) | Tracks system and user activities |

![Concept to Architecture Mapping](diagrams/concept-to-architecture-mapping.svg)

## Architecture Diagram

![Cognitive Hire Architecture](diagrams/sys-architecture.svg)

## Architecture Components

### 1. Security Framework
- **Authentication**: Azure AD B2C handles identity management with social login support
- **Authorization**: Custom RBAC implementation based on subscription plans and user roles
- **Data Protection**: Encryption at rest and in transit for all sensitive data
- **GDPR Compliance**: Built-in mechanisms for data erasure, export, and anonymization

### 2. Candidate Domain
Manages candidate profiles and core data:
- Profile management system
- Candidate data storage and retrieval
- Resume management
- Application tracking

### 3. Sourcing Domain
Handles job board integration, social media channels, referral programs, and talent pools:
- Job board integrations
- Social media sourcing tools
- Referral program management
- Talent pool organization

### 4. Screening Domain
Manages resume parsing, skills matching, automated assessments, and qualification verification:
- Automated resume parsing
- Skills matching algorithms
- **Interest Check workflows** (Email, SMS, Call outreach)
- Assessment delivery
- Qualification verification workflows
- **Candidate response tracking**

### 5. Employer Domain
Handles employer profiles, departments, and teams:
- Organization structure management
- Team hierarchies
- Department configurations
- Role definitions

### 6. Job Domain
Manages job definitions and core job data management:
- Job creation and editing
- Requirements management
- Job category organization
- Position tracking

### 7. Publishing Domain
Handles multi-channel distribution, job board posting, SEO optimization, and publishing analytics:
- Multi-channel job distribution
- Job board posting automation
- SEO optimization tools
- Publishing performance analytics

### 8. Recruitment Pipeline Domain
Orchestrates stage tracking, pipeline visualization, and transition rules:
- Recruitment stage definitions
- Pipeline visualization tools
- Stage transition automation
- Status tracking

### 9. Interview Domain
Manages interview feedback and evaluation:
- Interview scheduling tools
- Feedback collection forms
- Evaluation frameworks
- Decision tracking

### 10. Scheduling Domain
Handles availability management, timezone handling, resource allocation, and scheduling optimization:
- Calendar integration
- Availability management
- Timezone handling
- Resource allocation optimization

### 11. Communications Domain
Handles multi-channel notifications, templates, and triggers:
- Email delivery system
- SMS notification service
- Template management
- Communication triggers

### 12. Analytics Domain
Provides reporting, KPIs, and custom reports:
- Dashboard generation
- KPI tracking
- Custom report builder
- Data visualization tools

### 13. Financial Domain
Manages payments, subscriptions, and invoicing:
- Payment processing integration
- Subscription management
- Invoicing system
- Pricing tier enforcement

### 14. Compliance Domain
Ensures GDPR/CCPA adherence, regulatory monitoring, and policy enforcement:
- Compliance verification tools
- Regulatory requirement tracking
- Policy enforcement mechanisms
- Data protection measures

### 15. Audit Domain
Manages activity logging, change history, and accountability:
- Activity logging system
- Change history tracking
- User action audit trails
- Accountability reports

## Implementation Details

### 16. Technical Implementation
- **FastAPI Microservices**: Each service is implemented using FastAPI for high performance and native WebSocket support
- **Container Deployment**: Microservices are packaged as Docker containers and deployed to Azure Container Apps
- **Dual Protocol Support**: Each microservice exposes both REST endpoints and WebSockets
- **API Gateway Pattern**: Azure API Management provides a unified entry point for all services
- **Event-Driven Architecture**: Services communicate through events for asynchronous processing
- **Feature Flag Architecture**: Azure App Configuration with Feature Management provides centralized feature flag management for controlled rollouts, A/B testing, and environment-specific feature availability

### 17. Data Architecture

- **Polyglot Persistence**: Using the right database for each data type
  - **Cosmos DB** (NoSQL): For candidate profiles, workflow states, and event data
  - **PostgreSQL** (Relational): For organizational data, reporting, and transactions 
  - **Blob Storage**: For documents, resumes, and media files
- **Data Segregation**: Tenant isolation through database design

### 18. Agentic AI Framework

The Cognitive Hire platform uses **autonomous AI agents** as a key differentiator, enabling the automation of complex recruitment tasks that typically require human judgment. The agentic AI architecture consists of:

- **Agent Orchestration Layer**: Coordinates multiple specialized AI agents using LangGraph for complex multi-step workflows
- **Domain-Specific Agents**: Specialized AI agents for each recruitment domain with relevant tools and capabilities
- **Tool Integration**: Pre-built connectors to external systems like LinkedIn, email servers, and telephony services
- **Human-in-the-Loop**: Configurable approval workflows for critical decisions with human oversight

**Key Agent Applications**:

| Domain | Agent Capabilities | Integration Points |
|--------|-------------------|-------------------|
| Job Definition | - Generate job descriptions from basic requirements<br>- Refine and optimize job posting language<br>- Suggest skills based on market trends | Job Service |
| Candidate Sourcing | - Generate optimal search queries<br>- Web scrape professional networks<br>- Process candidate data from multiple channels<br>- Cross-reference with existing ATS data | Sourcing Service |
| Candidate Screening | - Match candidate skills to requirements<br>- Conduct automated initial outreach<br>- Perform preliminary phone screenings<br>- Analyze responses for qualification | Screening Service |
| Interview Scheduling | - Coordinate availability between parties<br>- Conduct scheduling conversations via phone/email<br>- Send confirmations and reminders<br>- Handle rescheduling requests | Scheduling Service |

### 19. Frontend Architecture

The Cognitive Hire platform includes three Next.js applications, each serving different user needs:

- **Main Recruitment Platform (PWA)**: For hiring managers and recruiters
- **Mobile Experience**: Responsive design optimized for mobile devices
- **Admin Portal**: For platform administrators and support staff

**Core Technologies**:

- **Next.js**: Full-stack React framework with built-in optimizations
- **TypeScript**: For type safety and improved developer experience
- **Redux Toolkit**: For centralized state management
- **React Query**: For server state management and data fetching
- **Material UI**: For component framework and design system
- **Azure Static Web Apps**: For hosting and global content delivery

**Frontend Architecture Patterns**:

1. **Atomic Design Methodology**:
   - Atoms (basic components)
   - Molecules (groups of atoms)
   - Organisms (groups of molecules)
   - Templates (page layouts)
   - Pages (specific instances of templates)

2. **Next.js App Router Structure**:
   ```
   /app                      # Next.js App Router structure
     /(auth)                 # Auth routes group
       login/page.tsx        # Login page
       register/page.tsx     # Registration page
     /(dashboard)            # Dashboard routes group
       jobs/                 # Job pages
       candidates/           # Candidate pages
       interviews/           # Interview pages
     /api                    # API routes
       jobs/route.ts         # Job API endpoints

   /components               # Reusable components
     /ui                     # Basic UI components
     /features               # Feature-specific components

   /lib                      # Shared utilities
     /api                    # API client
     /hooks                  # Custom hooks
     /types                  # TypeScript types
   ```

3. **API Access Pattern**:
   - React Query for data fetching, caching, and synchronization
   - Custom hooks for encapsulating API access
   - WebSocket integration for real-time updates
   - OpenAPI-generated TypeScript clients
   - Next.js API Routes for backend functionality

4. **Performance Optimizations**:
   - Server Components for reduced client JavaScript
   - Automatic code splitting at the page level
   - Image optimization with next/image
   - Static Site Generation (SSG) for public pages
   - Incremental Static Regeneration (ISR) for dynamic content
   - Server-side rendering (SSR) for personalized content

**Frontend Testing Strategy**:

- **Unit Tests**: Jest + React Testing Library
- **Component Tests**: Storybook for visual testing and documentation
- **E2E Tests**: Playwright for comprehensive cross-browser testing
- **Accessibility Testing**: axe-core integrated into development workflow

**Build and Deployment**:

- **Framework**: Next.js with built-in bundling and optimization
- **CI/CD Pipeline**: GitHub Actions (matching backend strategy)
- **Deployment Targets**: Azure Static Web Apps with global CDN

# Environment Strategy and Infrastructure as Code

## Relationship Between Components

1. **Docker Compose Setup**:

   This is not Terraform-related
   Used specifically for local development environments
   Provides developers with a consistent local setup that mirrors the architecture

2. **Environment Variables (.env files)**:

   Not Terraform-managed directly
   Application-level configuration (not infrastructure)
   In cloud environments, these would typically be injected via Azure App Configuration or environment variables set at the container level

3. **Setup Scripts (like setup-frontend-env.sh)**:

   Developer tooling, not Terraform
   Help automate consistent local environment setup
   Bridge between local development and the architecture patterns

## Where Terraform fits
According to your HLD, Terraform would be responsible for:

1. **Cloud Infrastructure**:

   Azure Container Apps for your microservices
   Azure AD B2C setup
   Azure SQL and Cosmos DB provisioning
   Networking and security configurations

2. **Environment-Specific Infrastructure**:

Different sizing/scaling for dev vs. test vs. production
Environment-specific security settings
Different instance counts and performance tiers

## Complete Environment Strategy
The overall pattern works like this:

   - Local Development: Docker Compose + .env files + setup scripts
   - Cloud Environments: Terraform + Azure DevOps/GitHub Actions + environment-specific tfvars

**Environment-Infrastructure Mapping**:

   | Environment | Infrastructure Provisioning | Configuration Management | Local Tools |
   |-------------|----------------------------|---------------------------|------------|
   | Development (Local) | N/A (local machine) | .env.development | Docker Compose |
   | Development (Cloud) | Terraform + dev.tfvars | Azure App Configuration | GitHub Actions |
   | Test | Terraform + test.tfvars | Azure App Configuration | GitHub Actions |
   | Production | Terraform + prod.tfvars | Azure Key Vault + App Configuration | GitHub Actions |


**Mock Services Integration**:

   Mock services are a key component of the local development environment and CI testing pipeline:

   | Environment | Real Services | Mock Services | Configuration |
   |-------------|---------------|---------------|--------------|
   | Development (local) | None | All | MSW browser mocks |
   | Development (Cloud) | Selected | Others | Docker mock containers |
   | Test | Most | Few | Containerized mocks as needed |
   | Production | All | None | N/A |

   **Mock Configuration Management**:
   - Local: Environment variable `USE_MOCKS=true` in `.env.development`
   - CI: Mock configuration via GitHub Actions variables
   - Development: Configurable mock endpoints for specific scenarios

# Design Decision Records (DDRs)

## DDR-001: Domain-Based Microservice Architecture

**Context**: Need to design a scalable system for recruitment workflow management.

**Decision**: Implement domain-based microservices with dual protocol support (REST + WebSockets).

**Rationale**:
- Aligns technical services with business domains for better organization
- Enables independent scaling of components based on demand
- Supports team autonomy with clear service boundaries
- Reduces cross-service communication compared to function-based microservices

**Implications**:
- Requires clear domain boundaries and service contracts
- Each team owns their domain's REST and WebSocket implementations
- More complex deployment compared to monolith

## DDR-002: FastAPI with Native WebSockets

**Context**: Need a high-performance backend that supports both traditional APIs and real-time updates.

**Decision**: Use FastAPI with native WebSocket support instead of a separate real-time service.

**Rationale**:
- FastAPI offers high performance and native async support
- Eliminates need for additional real-time communication services
- Reduces complexity and cost by leveraging one technology
- Direct WebSocket support simplifies the architecture

**Implications**:
- Team needs Python/FastAPI expertise
- Scalability for WebSockets requires careful implementation
- May need Redis for multi-instance WebSocket coordination later

## DDR-003: Containerization and Azure Container Apps

**Context**: Need a flexible deployment strategy for microservices.

**Decision**: Deploy FastAPI services as containers on Azure Container Apps instead of Azure Functions.

**Rationale**:
- Better support for long-lived WebSocket connections
- More flexible runtime environment than Azure Functions
- Cost-effective with scale-to-zero capability
- Simplifies local development and testing

**Implications**:
- Requires containerization knowledge
- Need for container orchestration strategy
- Container registry management

## DDR-004: GDPR-Compliant Data Architecture

**Context**: Need to handle personal data according to GDPR requirements.

**Decision**: Implement domain-specific GDPR compliance with different strategies for candidate vs. employer data.

**Rationale**:
- Candidates require complete data deletion capability
- Employer data needs preservation for audit trail with anonymization
- Different legal bases for processing different types of personal data
- Need to balance compliance with business continuity

**Implications**:
- More complex data models with soft deletion/anonymization
- Need for audit trails and consent tracking
- Cross-service data removal coordination

## DDR-005: Infrastructure as Code with Terraform

**Context**: Need reproducible and version-controlled infrastructure.

**Decision**: Use Terraform for infrastructure provisioning with GitHub Actions for automation.

**Rationale**:
- Declarative approach to infrastructure
- Provider-agnostic IaC solution
- Strong integration with GitHub Actions
- Supports environment consistency and repeatability

**Implications**:
- Learning curve for team
- Need for state management strategy
- Required planning for staged environment deployment

## DDR-006: Multi-Tier Deployment Strategy

**Context**: Need a cost-effective approach for a startup with growth potential.

**Decision**: Implement a phased deployment strategy with initial focus on core services.

**Rationale**:
- Minimizes initial cloud spend
- Allows for validated learning before full implementation
- Provides clear scaling path as business grows
- Preserves architectural integrity while deferring costs

**Implications**:
- Need for clear feature prioritization
- Architecture must support incremental deployment
- Some advanced features initially implemented with simpler alternatives

## DDR-007: Hierarchical Design Traceability Framework

**Context**: 
As we move from concept papers to high-level architecture to detailed implementation designs, we need a structured approach to maintain clear connections between these artifacts. Without explicit traceability, there's risk of implementation drift, knowledge silos, and inconsistent application of architectural principles.

**Decision**: 
Implement a hierarchical design traceability framework that explicitly links concept papers, high-level architecture components, low-level design specifications, and implementation through standardized documentation, visual modeling, API contracts, and code references.

**Rationale**:
- Creates a navigable path from architectural concepts to implementation details
- Ensures architectural decisions are consistently applied in implementation
- Supports onboarding by providing context for detailed designs
- Enables impact analysis when architectural changes are proposed
- Facilitates compliance with technical and regulatory requirements
- Improves maintainability by documenting design intent at all levels

**Implementation Tools**:
1. **Document Structure**:
   - Concept papers and diagrams stored in `/docs/architecture/` with version control
   - Architecture documents in `/docs/architecture/` with references to concept origins
   - Cross-references between concept and architecture documents
   - Markdown-based documentation with standardized templates
   - Architecture Decision Records (ADRs) at both HLD and LLD levels
   - GitHub Wiki for centralized documentation access

2. **Diagram Tools**:
   - **Draw.io/diagrams.net**: Primary diagramming tool with VS Code integration
   - **C4 Model Framework**: For hierarchical system visualization
   - **Mermaid JS**: For sequence diagrams embedded in markdown

3. **API Specification**:
   - **OpenAPI 3.0**: For REST API contracts
   - **AsyncAPI 2.0**: For WebSocket message definitions
   - **Swagger UI**: For interactive API documentation

4. **Code Documentation**:
   - **Python docstrings**: With architecture reference annotations
   - **JSDoc**: For frontend component documentation
   - **Type definitions**: To formalize data contracts

**Practical Examples**:

1. **Document Structure Example**:
```
/docs 
   /architecture 
     concept-paper.md            # Original concept documentation
     diagrams/concept.drawio     # Original concept visualization
     diagrams/concept-to-architecture-mapping.md  # Traceability map
     high-level-design.md        # References concept paper
     /low-level-design 
       /job-domain 
         README.md               # References both HLD and concept
         // ...other files...
```

2. **Concept-to-HLD Traceability Example**:
```
# Job Service - High Level Design Section

This component implements the "Publishing" capability
described in the Technology Concept (concept-paper.md)
and visualized in the concept diagram (diagrams/concept.drawio).

## Key Implementation Decisions
* Expanded the concept's basic publishing channels with SEO optimization
* Implemented analytics for publishing performance
```

## DDR-008: Traceability Framework Enforcement Mechanisms

**Context**: 
While DDR-007 establishes a comprehensive traceability framework, we need specific mechanisms to enforce and verify adherence to this framework across the development lifecycle. Without enforcement, the framework risks becoming aspirational rather than practical.

**Decision**: 
Implement automated and process-based enforcement mechanisms including PR templates, documentation linters, pre-commit hooks, and CI pipeline validations to ensure consistent application of the traceability framework defined in DDR-007.

**Rationale**:
- Manual adherence to architectural frameworks often degrades over time
- Automated enforcement ensures consistency across team members
- Provides measurable indicators of architectural compliance
- Early detection of traceability gaps reduces technical debt
- Integration with development workflow minimizes additional overhead

**Implementation Details**:

1. **Pull Request Template**:
   ```yaml
   # .github/pull_request_template.md
   ## Description
   ...

   ## Architectural Traceability
   - **Related Concept Element**: [e.g., Authentication, Scheduling]
   - **Related HLD Component**: [e.g., Security Framework, Scheduling Domain]
   - **Implements DDR**: [e.g., DDR-002]
   - **LLD Documents Updated**: [Y/N]
   - **Diagrams Updated**: [Y/N]

   ## Concept Impact Assessment
   - [ ] No impact on original concept
   - [ ] Enhances original concept
   - [ ] Deviates from original concept (explain below)

   ## Checklist
   - [ ] Code follows architectural patterns defined in HLD
   - [ ] API contracts maintain consistency with documentation
   - [ ] Documentation references updated
   - [ ] Concept-to-architecture mapping remains accurate
   ```

2. **Documentation Linter**:
   ```js
   // scripts/doc-linter.js
   const fs = require('fs');
   const path = require('path');
   const glob = require('glob');

   // Check for HLD references in LLD documents
   const checkHLDReferences = (filePath) => {
     const content = fs.readFileSync(filePath, 'utf8');
     if (!content.includes('high-level-design.md')) {
       console.error(`ERROR: ${filePath} is missing reference to HLD`);
       return false;
     }
     return true;
   };

   // Run on all LLD documents
   glob.sync('docs/architecture/low-level-design/**/*.md')
     .forEach(checkHLDReferences);
   ```

3. **Pre-Commit Hook**:
   ```sh
   #!/bin/sh
   # .git/hooks/pre-commit

   # Run documentation verification on changed markdown files
   git diff --cached --name-only | grep -E '\.(md|yaml)$' | xargs node scripts/doc-linter.js

   # Exit with error code if linter failed
   if [ $? -ne 0 ]; then
     echo "Documentation linting failed. Please fix issues before committing. Refer high-level-design.md for traceability enforcement."
     exit 1;
   fi
   ```

## DDR-009: Environment Consistency and Infrastructure Traceability

**Context**: 
Architectural decisions and traceability must extend beyond code to include infrastructure and environment configurations. Without consistency across local development, testing, and production environments, we risk architectural drift, environment-specific bugs, and deployment failures.

**Decision**: 
Implement a comprehensive environment strategy that ensures architectural consistency across all deployment targets through Infrastructure as Code (IaC), containerization, and environment-aware configuration management.

**Rationale**:
- "Works on my machine" problems often stem from environment inconsistencies
- Repeatable deployments require deterministic environment configurations
- Architecture patterns must be consistently implemented at infrastructure level
- Early detection of environment-specific issues reduces production risks
- Enables reliable testing of architectural characteristics (performance, security, etc.)

**Implementation Approach**:

1. **Environment Definition Framework**:
   - **Local Development**: Docker Compose for local microservices
   - **Testing**: Azure Container Apps with test-specific scaling
   - **Production**: Full Azure ecosystem with production scaling/redundancy
   - **All environments**: Defined via Terraform modules with environment-specific parameters

2. **Infrastructure as Code Requirements**:
   - All infrastructure defined in Terraform
   - Environment-specific variable files (`dev.tfvars`, `test.tfvars`, `prod.tfvars`)
   - Version-controlled infrastructure code with the same PR process as application code

3. **Local Development Environment**:
   ```yaml
   # docker-compose.yml template for local development
   version: '3.8'
   services:
     # Backend services as previously defined
     job-service:
       build: ./backend/job_service
       environment:
         - POSTGRES_HOST=db
         - AUTH_PROVIDER=mock # dev-only override
       depends_on:
         - db
     
     employer-service:
       build: ./backend/employer_service
       # Follows same architectural pattern as job-service
     
     # Database services
     db:
       image: postgres:13
       volumes:
         - postgres_data:/var/lib/postgresql/data
         
     # Frontend development service
     frontend:
       build: 
         context: ./frontend
         dockerfile: Dockerfile.dev
       volumes:
         - ./frontend:/app
         - /app/node_modules
       ports:
         - "3000:3000"
       environment:
         - REACT_APP_API_URL=http://localhost:8080
         - REACT_APP_AUTH_PROVIDER=mock-auth # dev-only
   ```

4. **Consistency Verification**:

   - Automated checks for environment parity
   - Configuration drift detection in CI/CD pipeline
   - Architecture compliance tests that run in all environments
   - Monitoring pattern consistency across environments

5. **Documentation Requirements**:

   - Each LLD must include environment-specific considerations
   - Infrastructure code must reference architectural decisions
   - Clear mapping between microservices and infrastructure components
   - Environment setup documentation for new team members

6. **Frontend Environment Configuration**:

   - Local Development:
      - React development server with hot-reloading
      - Environment-specific .env.development files
      - Mock authentication services for local development
      - Service worker disabled for development
   - Testing/Staging:
      - Production build with staging API endpoints
      - Azure Static Web App deployment
      - Test-specific feature flags enabled
      - Connected to test instances of Azure AD B2C
   - Production:
      - Production build with optimizations
      - CDN integration for static assets
      - Azure Front Door for global delivery
      - Production authentication configuration

7. **Frontend-Backend Integration Strategy**:
   - API URL configuration per environment
   - Consistent authentication flow across environments
   - Environment-aware feature flags
   - Development proxy for CORS and authentication handling
   - Mock API servers for disconnected frontend development

   Example React .env files:
   ```
   # .env.development
   REACT_APP_API_URL=http://localhost:8080
   REACT_APP_AUTH_CLIENT_ID=local-development-client-id
   REACT_APP_ENABLE_MOCK_AUTH=true

   # .env.test
   REACT_APP_API_URL=https://api-test.cognitivehire.com
   REACT_APP_AUTH_CLIENT_ID=test-client-id
   REACT_APP_ENABLE_MOCK_AUTH=false

   # .env.production
   REACT_APP_API_URL=https://api.cognitivehire.com
   REACT_APP_AUTH_CLIENT_ID=production-client-id
   REACT_APP_ENABLE_MOCK_AUTH=false
   ```

8. **Frontend Development Setup Script**:
   ```sh
   #!/bin/bash
   # scripts/setup-frontend-env.sh

   # Install dependencies
   cd frontend
   npm install

   # Copy environment template
   cp .env.development.template .env.development

   # Set up pre-commit hooks
   npx husky install

   # Start development server with backend integration
   npm run start:with-api
   ```

## DDR-010: API-First Development with Auto-Generated Mocks

**Context**: 
Developers need to work independently without waiting for dependent services to be implemented. Frontend teams need stable APIs to develop against, even when backend services are under development or unavailable in local environments.

**Decision**: 
Adopt an API-first development approach with auto-generated mock services derived directly from API specifications, enabling parallel development across teams.

**Rationale**:
- Decouples frontend and backend development timelines
- Ensures consistent API contracts between mock and real implementations
- Enables offline development without full infrastructure
- Provides stable testing environment for automated tests
- Reduces integration issues by testing against specification-accurate mocks

**Implementation Approach**:

1. **API-First Development Workflow**:
   - OpenAPI/AsyncAPI specifications must be created before implementation
   - API changes require specification updates before code changes
   - API review process includes frontend and backend stakeholders

2. **Mock Generation Strategy**:
   - **REST APIs**: Auto-generate from OpenAPI specs using MSW or Prism
   - **WebSockets**: Generate from AsyncAPI definitions using AsyncAPI tools
   - **Mock Data**: Use realistic data generators with configurable scenarios

3. **Mock Service Architecture**:
   - Local development: In-browser mocks using MSW
   - Integration testing: Containerized mock services
   - CI environment: Dedicated mock service containers

4. **Example MSW Setup for Frontend**:
   ```javascript
   // src/mocks/handlers.js
   import { rest } from 'msw'
   import { jobsData } from './data/jobs'

   export const handlers = [
   // Intercept job listing requests
   rest.get('/api/jobs', (req, res, ctx) => {
      // Return mock data based on OpenAPI schema
      return res(ctx.status(200), ctx.json(jobsData))
   }),
   
   // Mock authentication responses
   rest.post('/api/auth/login', (req, res, ctx) => {
      const { email } = req.body
      return res(
         ctx.status(200),
         ctx.json({
         user: {
            id: 'user-1',
            email,
            name: 'Test User',
         },
         token: 'mock-jwt-token',
         })
      )
   })
   ]
   ```

5. **Mock Auto-Generation Process**:

   - **OpenAPI-to-Mock Pipeline**:
     ```
     OpenAPI Spec → Validation → Mock Generator → Mock Server/Client
     ```

   - **Tools for Auto-Generation**:
     - **Prism**: `prism mock -p 4010 ./api-specs/job-api.yaml`
     - **MSW**: Using OpenAPI-to-MSW converter
     - **Mirage.js**: For client-side mocks with schemas

   - **CI Pipeline Integration**:
     ```yaml
     # In GitHub Actions workflow
     steps:
       - name: Generate mock services
         run: |
           for spec in ./api-specs/*.yaml; do
             docker run --rm -v $(pwd)/api-specs:/specs stoplight/prism:4 \
               mock -p 4010 "/specs/$(basename $spec)" > mock-$(basename $spec .yaml).log &
           done
     ```

6. **Version Control Strategy**:
   - API specifications stored in service-specific `/api` directories (e.g., `/backend/screening-service/api/`)
   - Generated mock configurations in `/mocks` directory
   - Mock data templates in `/mocks/data`

7. **API-First Enforcement Mechanisms**:

   - **OpenAPI Validation Middleware**:
     ```python
     # In FastAPI application startup
     from fastapi.openapi.utils import get_openapi
     import yaml
     
     # Load spec from file at startup
     with open("api/openapi.yaml") as f:
         api_spec = yaml.safe_load(f)
     
     # Override generated schema with file-based one
     def custom_openapi():
         return api_spec
     
     app.openapi = custom_openapi
     ```

   - **Automated Spec vs. Implementation Testing**:
     ```python
     # In test suite
     def test_api_matches_spec():
         """Test that FastAPI's generated OpenAPI matches our spec file"""
         with open("api/openapi.yaml") as f:
             expected_spec = yaml.safe_load(f)
         
         # Get the OpenAPI spec that would be generated from code
         actual_spec = get_openapi(
             title=app.title,
             version=app.version,
             routes=app.routes
         )
         
         # Compare paths, parameters, etc.
         assert actual_spec["paths"] == expected_spec["paths"]
     ```
   
   - **CI/CD Pipeline Enforcement**:
     - Pre-commit hook to validate API changes against spec
     - PR check that fails if implementation doesn't match spec
     - Automated test to compare generated spec against file spec

   - **Development Workflow Requirements**:
     - API changes must first be made to YAML specs
     - Implementation must then be updated to match specs
     - No direct changes to API surface without spec updates
     - Regular synchronization checks to ensure alignment
     
8. **Implementation Options**:

   - **Strict Enforcement**: 
     - API gateway validates all requests/responses against spec at runtime
     - Generated server code from specs (more common in Java/.NET)
     - CI pipeline fails if implementation deviates from spec

   - **Guided Enforcement** (Recommended):
     - Spec changes require approval before implementation
     - Automatic tests verify conformance 
     - Warnings (not failures) during development
     - Hard failures in CI/CD pipeline

## DDR-011: Feature Flag Architecture

**Context**: 
Modern application development requires the ability to selectively enable features across environments, conduct A/B testing, and control feature rollout without redeploying code. Our current environment strategy mentions feature flags but lacks a comprehensive approach to implementation and management.

**Decision**: 
Implement a centralized feature flag service using Azure App Configuration with Feature Management extension, integrated with both frontend and backend services.

**Rationale**:
- Supports multiple environments with different flag configurations
- Allows A/B testing and experimentation
- Provides runtime toggling without redeployment
- Facilitates testing of features in isolation

**Implementation Approach**:
1. Azure App Configuration with Feature Management (Recommended)

   Pros: Integrates with your Azure ecosystem, managed service, reasonable free tier
   Pricing: Free tier includes 1,000 requests per day, then $0.085 per 10,000 operations
   Integration: Native .NET and JavaScript libraries

2. Flagsmith (Open Source Alternative)

   Pros: Self-hostable for cost control, can migrate to cloud later
   Pricing: Self-hosted is free, managed starts at $45/month
   Integration: REST APIs and SDKs for multiple languages

3. ConfigCat (Simple Solution)

   Pros: Simple setup, 10 flags free forever
   Pricing: Free tier, then $21/month for more features
   Integration: SDKs for 10+ platforms

## DDR-012: Agentic AI Architecture for Recruitment Automation

**Context**: 
Traditional recruitment software focuses on workflow management and data organization but still requires significant human effort for qualitative tasks like job creation, sourcing, screening, and coordination. The market opportunity exists for a system that can perform these tasks autonomously at scale.

**Decision**: 
Implement a multi-agent AI architecture using Microsoft AutoGen and Azure OpenAI Service to create autonomous AI agents that can perform complex recruitment tasks with minimal human intervention.

**Rationale**:
- Reduces time-to-hire by automating labor-intensive tasks
- Increases candidate quality through consistent, bias-aware screening
- Scales recruiting capacity beyond human limitations
- Creates a significant market differentiator against traditional ATS systems
- Leverages latest advancements in LLM capabilities and agent frameworks
- Better integration with our Azure-centric architecture
- Simplified development with a single unified agent framework

**Implementation Approach**:

1. **Core Agent Framework**:
   - **Microsoft AutoGen**: Primary framework for building and orchestrating multiple agent workflows
   - **Azure OpenAI Service**: For production-grade LLM capabilities with enterprise security
   - **Custom Agent Extensions**: For recruitment-specific capabilities not covered by AutoGen
   - **Semantic Kernel (if needed)**: For specialized memory and contextual reasoning capabilities

2. **Agent Architecture Patterns**:

   a. **Job Definition Agents**:
      - Uses fine-tuned LLMs trained on high-quality job descriptions
      - Implements ReAct pattern for iterative job description refinement
      - Ingests company data, role requirements, and industry standards
      - Provides multiple drafts with A/B testing capabilities

   b. **Sourcing Agents**:
      - Implements web navigation tools using Playwright/Puppeteer
      - Uses RAG with vector embeddings for candidate-role matching
      - Maintains session state for complex multi-platform searches
      - Includes ethical scraping protocols and rate limiting

   c. **Screening Agents**:
      - Multi-modal capability for CV parsing and analysis
      - Conversation agents for SMS, email, and voice interactions
      - Azure Communication Services for telephonic assessments
      - Sentiment analysis and qualification scoring

   d. **Scheduling Agents**:
      - Calendar API integrations (Google, Outlook, etc.)
      - NLP for availability extraction from conversations
      - Optimization algorithms for interview panel coordination
      - Voice synthesis for phone confirmations

3. **Agent Tool Integration**:

   - **LinkedIn Automation**: Selenium-based tools with proxy rotation
   - **Email Processing**: Azure Communication Services for email interactions
   - **Phone Interaction**: Azure Communication Services for voice capability
   - **Web Scraping**: Custom tools with CloudFlare bypass techniques
   - **Document Processing**: Azure Form Recognizer for CV parsing
   - **Geographic Tools**: Location-based search optimization

4. **Monitoring and Governance**:

   - Comprehensive agent action logging
   - Human-readable explanations for all agent decisions
   - Performance metrics for continuous improvement
   - Compliance with recruitment regulations
   - Bias detection and mitigation systems

**Architecture Considerations**:

1. **Why AutoGen Over LangChain/LangGraph**:
   - **Simplified Stack**: Single framework instead of multiple frameworks
   - **Azure Integration**: Native integration with our Azure services
   - **Multi-agent First**: Designed from the ground up for conversational agents
   - **Enterprise Readiness**: Microsoft's enterprise focus aligns with our production needs
   - **Human-in-the-Loop**: Strong support for human approval workflows

2. **Implementation Tradeoffs**:
   - May require building custom tools for some recruitment workflows
   - Need to implement certain patterns that LangChain provides out-of-the-box
   - Will benefit from Microsoft's roadmap and updates for enterprise AI

**Technical Requirements**:

1. **Agent Development and Testing Framework**:
   - Agent simulation environment for testing
   - CI/CD pipeline for agent deployment
   - A/B testing framework for agent performance
   - Unit tests for individual agent tools

2. **Security and Compliance**:
   - Encryption for all candidate data
   - GDPR-compliant data handling
   - Role-based access controls
   - Audit logs for all agent actions

3. **Performance Requirements**:
   - Horizontal scaling for concurrent agent tasks
   - Caching for common agent requests
   - Asynchronous processing for long-running tasks
   - Rate limiting to respect external API constraints

**Implications**:
- Significant AI expertise required for development team
- Higher cloud computing costs compared to traditional systems
- Ongoing training and monitoring needed for agent effectiveness
- Need for careful ethical guidelines and human oversight
- Integration complexity with external platforms

**Risk Mitigation**:
- Initially deploy with human-in-the-loop for all critical decisions
- Progressively increase autonomy as reliability is proven
- Maintain alternative manual workflows for all agent processes
- Regular monitoring for compliance with platform policies (LinkedIn, etc.)
- Transparency with candidates about AI interaction points

## DDR-013: Shared Schema Definitions for Backend-Frontend Type Safety

**Context**: 
When data structures are defined separately in backend and frontend code, discrepancies can arise leading to runtime errors. These errors are difficult to catch without comprehensive integration testing. As our system evolves, the risk of mismatched data structures between services increases.

**Decision**: 
Implement an OpenAPI-driven schema definition system where backend Pydantic models are the source of truth, automatically generating TypeScript interfaces for frontend consumption.

**Rationale**:
- Ensures single source of truth for data structures
- Catches breaking changes at build/compile time rather than runtime
- Reduces manual synchronization effort between teams
- Leverages existing FastAPI/Pydantic capabilities
- Complements our existing API-first approach (DDR-010)

**Implementation Approach**:

1. **Source of Truth**: 
   - Backend Pydantic models serve as the definitive schema
   - FastAPI auto-generates OpenAPI specifications
   - Models include complete validation rules and descriptions

2. **TypeScript Generation Pipeline**:
   - Extract OpenAPI schemas from each service during build
   - Use `openapi-typescript` to generate TypeScript interfaces
   - Include generation in CI/CD pipeline

3. **Integration Process**:
```
Backend Pydantic Models → FastAPI OpenAPI Generation → Extracted Schema Files → TypeScript Interface Generation → Frontend Type Imports
```

4. **Breaking Change Detection**:
   - Git-based diff checks for interface changes
   - CI failure on potential breaking changes (e.g., removed fields)
   - Automated PR comments highlighting schema changes

5. **Developer Workflow**:
   - Update Pydantic models in backend
   - CI automatically generates updated TypeScript
   - Typescript compiler flags incompatible usages in frontend
   - Type errors block build if frontend doesn't adapt to changes

**Tooling**:

- **Backend**: FastAPI + Pydantic (already in architecture)
- **Schema Extraction**: Custom scripts or FastAPI CLI
- **TypeScript Generation**: `openapi-typescript`
- **Integration**: GitHub Actions within existing CI

**Example**:

Backend model (Python):
```python
class CandidateProfile(BaseModel):
    id: str
    name: str
    email: EmailStr
    experience_years: int
    skills: List[Skill]
    created_at: datetime
```

Generated TypeScript interface:
```typescript
export interface CandidateProfile {
  id: string;
  name: string;
  email: string; // Validated as email in runtime
  experience_years: number;
  skills: Skill[];
  created_at: string; // ISO datetime string
}
```

**Implications**:
- Requires discipline to keep backend models as source of truth
- Adds steps to CI/CD pipeline
- May introduce complexity for handling certain TypeScript-specific idioms
- Potential for false positives on breaking changes

## DDR-014: Next.js Frontend Framework Adoption

**Context**: 
The frontend architecture requires a framework that supports modern web application needs including SEO optimization, server-side rendering, and optimal performance. The initial design considered React with Vite for frontend development, but a comprehensive assessment of long-term needs is required before implementation begins.

**Decision**: 
Adopt Next.js as the primary frontend framework instead of the previously planned React + Vite combination.

**Rationale**:
- Better SEO capabilities through server-side rendering and static generation
- Improved performance through automatic code splitting and optimizations
- Built-in API routes eliminate need for separate backend for simple functionality
- Enhanced developer experience with file-based routing
- Enterprise-ready framework with strong industry adoption
- Simplified deployment model
- Reduced client-side JavaScript with Server Components
- Better image optimization out-of-the-box

**Implementation Approach**:

1. **Application Structure**:
   - Use Next.js App Router for modern React server components
   - Structure routes using the Next.js file-based routing system
   - Leverage directory grouping patterns for logical organization

2. **Performance Features**:
   ```
   React Client Components: For interactive UI with client state
   React Server Components: For static/dynamic server-rendered content
   Static Site Generation: For public, cacheable content 
   Server-Side Rendering: For dynamic, personalized pages
   API Routes: For backend functionality alongside frontend code
   ```

3. **Integration with Backend Services**:
   - Maintain existing WebSocket strategy using client-side hooks
   - Use Server-Side rendering to fetch initial data directly from backends
   - Implement BFF (Backend for Frontend) pattern with API Routes where beneficial

**Technical Requirements**:

1. **Development Environment**:
   - Next.js development server for local development
   - API mocking strategy compatible with Next.js
   - Integration with existing schema generation pipeline

2. **Deployment Strategy**:
   - Azure Static Web Apps for Next.js applications
   - Static exports for purely static pages
   - Azure CDN for optimal global content delivery

3. **Testing Approach**:
   - Unit testing with Jest
   - Integration testing with React Testing Library
   - E2E testing with Playwright
   - Server component testing strategy

**Implications**:
- Learning curve for developers not familiar with Next.js patterns
- Adaptation of existing authentication flows to Next.js patterns
- Need to configure API routes securely
- New build optimization and deployment patterns

**Benefits**:
- Faster time-to-market with built-in capabilities
- Improved SEO for job listings and company pages
- Better performance on mobile devices
- Simplified architecture with combined frontend/BFF capabilities

## DDR-015: Code-Adjacent Documentation Strategy

**Context**: 
Traditionally, architecture and design documentation has been stored separately from implementation code, leading to documentation drift, reduced visibility, and maintenance challenges. As teams began implementing services based on the LLD documents, we observed increasing divergence between documented design and actual implementation.

**Decision**: 
Migrate from architecture-focused documentation in a centralized location to code-adjacent documentation stored alongside the implementation code in each service repository, while maintaining high-level architecture documentation centrally.

**Rationale**:
- Documentation is more discoverable when placed beside the code it describes
- Developers are more likely to update documentation when making code changes if it's in the same location
- Pull requests can include both code and documentation updates, ensuring they remain in sync
- Service owners can control their own documentation without depending on a central team
- Reduces duplication and single-source-of-truth issues between architecture and implementation
- Better supports agile development practices by keeping documentation lean and relevant

**Implementation**:
- Service documentation will follow a standardized structure in a `/docs` folder within each service
- API contracts will be stored in an `/api` folder within each service
- High-level architecture concerns remain in the central architecture repository

**Implications**:
- Teams need to complete documentation migration as they implement services
- Cross-service documentation requires special attention to avoid fragmentation
- Architects must still review service-level documentation for architectural compliance
- Documentation tooling may need to be updated to discover and compile distributed documentation
- Onboarding processes should be updated to reflect the new documentation approach

**References**:
- [Screening Service Documentation](../../backend/screening-service/docs/README.md) (first implemented service)

## DDR-016: Authentication Bypass Implementation

**Context:**
During development and testing, it's necessary to provide a mechanism for bypassing authentication while maintaining security in production.

**Decision:**
Implement a configurable authentication bypass with the following characteristics:
- Controlled by environment configuration (`AUTH_BYPASS_ENABLED` flag)
- Only available in development and testing environments
- Requires a valid bypass token in the `X-Auth-Bypass` header that matches the configured token
- Provides transparent API testing experience in Swagger UI through OpenAPI integration

**Implementation:**
1. Config-based toggle (`AUTH_BYPASS_ENABLED=True/False`)
2. Token validation against `AUTH_BYPASS_TOKEN` environment variable
3. OpenAPI schema integration for Swagger UI authentication
4. Request header-based authentication (`X-Auth-Bypass`)
5. Mock user/tenant context injection when bypassed

**Benefits:**
- Simplified developer testing without compromising production security
- Standardized bypass mechanism across services
- Transparent tenant context simulation with `X-Test-Tenant-ID`
- No auth bypass in production regardless of configuration

