# Implementation Plan and Next Steps

Based on the comprehensive architecture and high-level design documented in [high-level-design.md](high-level-design.md), this document outlines practical implementation considerations and next steps.

## Service Modeling Considerations

### Domain-to-Container Mapping Strategy

**Question**: Will each domain be a container that is deployed? Will 15+ containers be too many for maintenance and infrastructure costs?

**Recommendation**: Implement a **logical-to-physical domain consolidation** approach for optimal balance between separation of concerns and operational efficiency.

#### Preferred Container Grouping:

| Deployment Unit | Contained Domains | Rationale |
|-----------------|-------------------|-----------|
| **Candidate Service** | - Candidate Domain | Core candidate profile management |
| **Recruitment Service** | - Employer Domain<br>- Sourcing Domain<br>- Screening Domain<br>- Job Domain<br>- Publishing Domain | These domains deal with employer needs, job definition, and candidate evaluation |
| **Workflow Service** | - Recruitment Pipeline Domain<br>- Interview Domain | These domains manage the candidate journey |
| **Scheduling Service** | - Scheduling Domain | Scheduling has unique technical requirements (calendar integration) |
| **Communications Service** | - Communications Domain | Centralized notification handling |
| **Support Services** | - Analytics Domain<br>- Financial Domain<br>- Compliance Domain<br>- Audit Domain | Administrative and governance functions |
| **Security Service** | - Security Framework | Authentication, authorization, and data protection |

This consolidation reduces the number of containers from 15+ to 7, providing an optimal balance of:
- Maintainability (fewer services to manage)
- Cost efficiency (fewer container instances)
- Logical separation (domains with similar functions grouped together)
- Performance (reduced inter-service communication for related functions)

#### Implementation Notes:

1. **Internal Domain Structure**: Each physical service should maintain clear internal boundaries between domains
2. **Shared Libraries**: Create domain-specific shared libraries that can be used across physical services
3. **Database Separation**: Maintain separate logical database schemas even within consolidated services
4. **Cost Impact**: This consolidation aligns with the cost estimates in [cost-estimate.md](cost-estimate.md), potentially reducing the estimated Container Apps costs

### Centralized Logging and Observability

**Recommendation**: Implement a standardized observability framework across all services.

#### Key Components:

1. **Structured Logging Standard**:
   - Common log format across all services
   - Mandatory fields: timestamp, service name, correlation ID, severity
   - Context-enriched logs (user ID, tenant ID, operation name)

2. **Centralized Log Processing**:
   - Azure Application Insights for application telemetry
   - Log Analytics Workspace for aggregation
   - OpenTelemetry instrumentation for consistent collection

3. **Observability Pipeline**:
   ```
   Service Logs → OpenTelemetry SDK → Azure App Insights → Log Analytics → Dashboards
   ```

4. **Implementation Approach**:
   - Create a shared logging library used by all services
   - Implement middleware that automatically adds correlation IDs
   - Configure consistent retention and sampling policies

5. **Cost Management**:
   - Implement log level filtering at source
   - Use sampling for high-volume transaction paths
   - Configure workspace-level retention policies

### Cross-Domain Service Interactions

**Recommendation**: Implement a hybrid communication pattern based on interaction type.

#### Communication Patterns:

1. **Synchronous Patterns** (for immediate responses):
   - REST APIs for direct queries
   - GraphQL for complex data requirements
   - gRPC for high-performance internal service communication

2. **Asynchronous Patterns** (for eventual consistency):
   - Event Grid for event broadcasting
   - Service Bus for reliable queuing and message delivery
   - Event-driven transactions for cross-domain processes

#### Implementation Guidelines:

1. **API Gateway**: Implement Azure API Management as the single entry point
2. **Service Discovery**: Use Container Apps built-in service discovery
3. **Circuit Breaking**: Implement resilience patterns for all cross-domain calls
4. **Versioning Strategy**: Explicit API versioning for all inter-service APIs
5. **Contract Testing**: Implement consumer-driven contract tests for service interfaces

### User Identity and Database Mapping

**Question**: How to tie back the OAuth logged-in user to the app's structured database and unstructured datastore?

**Recommendation**: Implement a **federated identity model** with internal user records.

#### Implementation Approach:

1. **Primary Identity Schema**:
   ```
   User {
     internalId: UUID (primary key),
     identityProvider: String (e.g., "azure_ad_b2c", "google"),
     externalId: String (the OAuth provider's ID),
     email: String (normalized email address),
     emailVerified: Boolean,
     createdAt: Timestamp,
     lastLoginAt: Timestamp,
     userType: Enum ("candidate", "recruiter", "admin")
   }
   ```

2. **User Profile Relationship**:
   - Maintain separate `CandidateProfile` or `RecruiterProfile` tables
   - Link to core User record via `internalId` (your system's primary key)
   - Store profile details separate from identity information

3. **Identity Resolution Flow**:
   ```
   OAuth Login → Get External ID → Look up Internal User → 
   Create If Not Exists → Generate Session With Internal ID
   ```

4. **Database Design Considerations**:
   - Index on `(identityProvider, externalId)` for fast lookups
   - Index on normalized `email` for secondary lookups
   - Maintain audit history for identity changes

5. **Unstructured Data Mapping**:
   - Use internal IDs as keys in Cosmos DB documents
   - Include tenant information for multi-tenant isolation
   - Consider materialized views for frequently accessed identity-related fields

## Recommended Service Implementation Order

After careful analysis of the system architecture, domain dependencies, and critical functionality, here is the recommended order for service implementation:

### 1. Security Service (First Priority)

**Rationale for implementing first:**
- Provides the authentication foundation needed by all other services
- Establishes the identity model that will be referenced throughout the system
- Enables early integration and testing with Azure AD B2C
- Allows developers to use the auth bypass mechanism (DDR-016) during development of other services

**Initial scope:**
- Azure AD B2C integration with multi-tenant support
- User identity management with the federated model
- Role and permission framework implementation
- Authentication bypass for development environments
- Integration with database for user profile storage

**Technical dependencies:**
- Azure AD B2C tenant setup
- Postgres database for user records
- Docker container setup for local development

### 2. Candidate Service (Second Priority)

**Rationale for implementing second:**
- Represents the core entity (candidates) in the recruitment system
- Minimal dependencies on other domains
- Provides fundamental data needed by later services
- Enables early testing of the full authentication flow with actual user profiles

**Initial scope:**
- Basic candidate profile CRUD operations
- Resume storage and management
- User registration flow integration with Security Service
- Simplified candidate search functionality

**Technical dependencies:**
- Security Service for authentication
- Blob Storage for resume documents
- Postgres database for structured profile data

### 3. Recruitment Service - Job Domain Focus (Third Priority)

**Rationale for implementing third:**
- Jobs are required before implementing other recruitment functions
- Enables the core employer-side functionality
- Provides a foundation for the AI capabilities in job description creation
- Sets up the data models needed for later services (screening, sourcing, etc.)

**Initial scope:**
- Job creation and management
- Basic company/employer profile management
- Job categorization and tagging
- Simple job search and filtering
- Initial integration with Azure OpenAI for job description generation

**Technical dependencies:**
- Security Service for authentication
- Postgres database for job and employer data
- Initial Azure OpenAI integration

### Subsequent Phases

After the initial three services are implemented, subsequent phases should follow this order:

1. **Communications Service** - To enable notifications across the platform
2. **Workflow Service** - To implement the recruitment pipeline management
3. **Support Services** - Starting with analytics for data visibility
4. **Scheduling Service** - To complete the end-to-end candidate journey

## Next Steps in Implementation Journey

### 1. Service Foundation Setup

1. **Create API Specifications**:
   - Define OpenAPI specifications for each service
   - Document domain models and relationships
   - Establish API standards and conventions

2. **Set Up Development Environment**:
   - Docker Compose for local service orchestration
   - Local development database setup
   - Authentication bypass for development (as detailed in DDR-016)

3. **Implement Core Shared Libraries**:
   - Logging framework implementation
   - Authentication/authorization libraries
   - Common utilities and middleware

### 2. Infrastructure Setup

1. **Deploy Terraform Foundation**:
   - Core infrastructure components
   - Networking and security configuration
   - Container registry and environments

2. **CI/CD Pipeline Configuration**:
   - GitHub Actions workflows for build and deploy
   - Environment promotion strategy
   - Testing automation

3. **Monitoring and Alerting**:
   - Application Insights setup
   - Dashboard configuration
   - Alert rules and notification channels

### 3. First Service Implementation

Recommended initial services (based on core functionality):
- Security Service (Auth)
- Candidate Service
- Recruitment Service (focusing initially on Job Domain)

For each service:
1. Create service skeleton with FastAPI
2. Implement database migrations
3. Implement core CRUD operations
4. Add authentication and authorization
5. Implement domain-specific business logic
6. Add integration tests

### 4. Frontend Foundation

1. **Next.js Project Setup**:
   - Configure Next.js App Router structure
   - Set up TypeScript configuration
   - Implement design system foundation

2. **Authentication Flow Implementation**:
   - MSAL integration as described in DDR-016
   - Login and registration flows
   - Role-based access control

3. **Core UI Components**:
   - Implement Atomic Design components
   - Create layout templates
   - Add responsive design foundations

### 5. Incremental Feature Implementation

Follow an iterative approach:
1. Select the next highest priority service
2. Implement backend functionality
3. Create corresponding frontend components
4. Test end-to-end functionality
5. Deploy to development environment
6. Gather feedback and iterate

## Technical Proof-of-Concept Priorities

Before full implementation, consider these targeted proof-of-concepts:

1. **Authentication Integration**: Validate Azure AD B2C with both backend and frontend
2. **Container Communication**: Test inter-service communication patterns
3. **Database Performance**: Validate PostgreSQL and Cosmos DB performance with expected data patterns
4. **AI Integration**: Test Azure OpenAI Services integration for core AI capabilities
5. **Scaling Behavior**: Verify Container Apps scale-to-zero and scaling performance

## Conclusion

This implementation plan provides a structured approach to transform the architectural vision into a tangible system. By addressing key concerns around service organization, logging, cross-domain communication, and identity management upfront, the implementation can proceed more efficiently and avoid common pitfalls.

The proposed consolidated service approach balances architectural purity with practical operational concerns, reducing the total number of containers to 7 while maintaining clear domain boundaries. The suggested next steps provide a logical progression from infrastructure to core functionality, enabling incremental value delivery.

### Next Steps for First Service Implementation

## Cross-Service Security Implementation

### Security Service Role vs. API Security Decoration

While the Security Service is implemented as a separate physical service, security is implemented across all services through a combination of centralized authentication and distributed authorization:

#### 1. Authentication Flow

1. **Centralized Token Issuance**:
   - The Security Service (integrated with Azure AD B2C) handles user authentication
   - It issues signed JWT tokens containing claims about the user (identity, roles, permissions)
   - These tokens are then used across all other services

2. **Distributed Token Validation**:
   - Each service independently validates the JWT token using shared libraries
   - No direct dependency on the Security Service for runtime validation
   - Token validation happens locally using the JWT signature and public keys

#### 2. API Security Decoration

All service APIs will be decorated with security using a consistent pattern:

```python
# Example FastAPI endpoint with security decoration
from fastapi import FastAPI, Depends, HTTPException
from common_lib.auth import validate_token, require_permission

app = FastAPI()

# Middleware validates the JWT token (no call to Security Service)
@app.get("/api/jobs")
async def get_jobs(
    # Token validation happens locally in middleware
    token_data = Depends(validate_token),
    # Permission check happens locally based on token claims
    _permit = Depends(require_permission("jobs:read"))
):
    # Token is valid and has required permission
    return {"jobs": get_jobs_from_database()}
```

#### 3. Shared Security Libraries

To ensure consistent security implementation, a shared security library will be created:

1. **Common Auth Library**:
   - Token validation logic
   - Permission checking logic
   - Role-based access control helpers
   - Integration with Azure AD B2C token validation
   - Development bypass mechanism

2. **Security Middleware**:
   - FastAPI middleware for automatic token validation
   - Automatic logging of auth events
   - Context propagation (user ID, correlation ID)
   - Performance monitoring for auth operations

#### 4. Identity Propagation Between Services

When services call other services internally:

1. **Token Propagation**:
   - The original user token is passed between services
   - Each service validates the token independently
   - No new token issuance required for service-to-service calls

2. **Service-to-Service Authentication** (when needed):
   - For background processes or system actions, services use service principals
   - Managed identities are used where possible
   - Clear distinction between user-initiated and system-initiated actions

#### 5. Authorization Approaches

Three levels of authorization checks are implemented:

1. **Token-Based Authorization**:
   - Claims in the JWT token (roles, permissions) 
   - Local validation without external calls
   - Fastest performance, suitable for coarse-grained permissions

2. **Database-Based Authorization**:
   - Permissions stored in the service's database
   - Used for more granular or dynamic permissions
   - May require database lookups but no cross-service calls

3. **Resource-Based Authorization**:
   - Checks if the user has permission for a specific resource
   - Combines token claims with resource metadata
   - May need additional service-local database queries

#### 6. Implementation Example

```python
# In a FastAPI service endpoint
@app.get("/api/jobs/{job_id}")
async def get_job(
    job_id: str,
    # Validate JWT token (from common_lib)
    token_data = Depends(validate_token),
    # Check if user has job:read permission (from common_lib)
    _basic_permit = Depends(require_permission("job:read"))
):
    # Get the job from database
    job = await job_repository.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Resource-based permission check - verify user can access this specific job 
    # based on ownership or organization membership
    if not await job_permission_service.can_access_job(token_data.user_id, job):
        raise HTTPException(status_code=403, detail="Not authorized to access this job")
    
    return job
```

#### 7. Security Configuration Management

Since security configuration is shared across services:

1. **Centralized Configuration**:
   - Security settings stored in Azure App Configuration
   - Each service loads configuration at startup
   - Updates propagated consistently across all services

2. **Security Policy Distribution**:
   - General policies defined in the Security Service
   - Policies distributed as configuration rather than runtime dependencies
   - Service-specific policies extend the general policies

This approach ensures that while the Security Service is a separate physical service responsible for authentication and identity management, the security enforcement happens at each service boundary through shared libraries and consistent patterns. This provides both strong security and high performance without creating runtime dependencies between services for every API call.
