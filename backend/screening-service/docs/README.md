# Screening Service

## Overview
This service implements the candidate evaluation capabilities described in the concept paper's "Screening" and "Shortlisting" sections. It's responsible for evaluating candidate qualifications through two primary approaches:

### Screening Types

1. **Light Screening**: 
   - Part of the sourcing process
   - Involves searching for keywords online and scraping publicly available candidate data
   - Creates preliminary candidate profiles from external sources
   - Less resource-intensive, used for initial candidate discovery
   - No resume submission required from the candidate

2. **Deep Screening**:
   - More comprehensive candidate evaluation
   - Processes resumes submitted directly by candidates through job applications
   - Can also analyze resumes from the employer's existing resume store or this platform's resume store
   - Access to employer or platform resume stores depends on the organization's subscription plan
   - Includes detailed skills matching, interest checks, and assessments

The system automatically selects the appropriate screening approach based on:
- The organization's subscription plan
- The configured recruitment workflow
- The source of the candidate (direct application vs. sourced)

## Component Mapping to Concept Elements

| Concept Element | Implementation Component | Description |
|-----------------|--------------------------|-------------|
| Keyword-based filtering | `SkillsMatcher` service | Implements exact and fuzzy keyword matching from resumes to job requirements |
| Semantic analysis | `SemanticAnalyzer` service | Uses embeddings and NLP to match conceptually related skills and experiences |
| Hybrid approaches | `HybridMatcher` service | Combines keyword and semantic approaches for optimal skill matching |
| Light screening | `CandidateDiscoveryService` | Performs online searching and data scraping for candidate sourcing |
| Deep screening | `ResumeProcessingEngine` | Processes candidate-submitted or stored resumes |
| Interest Check phase | `InterestCheckManager` service | Implements the outreach workflows through email, SMS, call, and LinkedIn |
| Assessment phase | `AssessmentEngine` service | Delivers and processes candidate skills assessments |

## Design Decisions

### 1. Tiered Resume Parsing Approach

We implement a cost-efficient tiered approach:

1. **Text-based Parser (Primary)**: Handles ~80% of well-structured documents
2. **Form Recognizer (Secondary)**: For complex formatting when text-based parsing is insufficient
3. **Vision AI (Tertiary)**: Only for problematic documents like handwritten notes or damaged scans

This approach balances accuracy with cost-efficiency, reducing parsing costs by ~20%.

### 2. Skill Matching Methodology

We implement a hybrid skill matching system that combines:
- Exact keyword matching with synonym expansion
- Semantic similarity using embeddings from Azure OpenAI
- Experience level quantification and verification
- Contextual understanding of skills usage

### 3. Interest Check Workflow

We provide a flexible multi-channel approach for candidate outreach:
- Support for email, SMS, call, and professional network messages
- Automated response tracking and follow-up scheduling
- Integration with Communications Domain for message delivery
- Analytics on response rates by channel and message type

### 4. Phone Assessment Implementation

Our phone assessments use AI agents to:
- Conduct initial screening calls
- Follow standardized assessment scripts
- Analyze candidate responses
- Schedule callbacks when needed
- Generate assessment reports

## Technical Architecture

See [component-design.md](./component-design.md) for detailed component architecture.

## Key Workflows

1. **Resume Processing Workflow**: Upload → Parse → Extract → Match
2. **Interest Check Workflow**: Select Candidates → Send Outreach → Track Responses → Evaluate Interest
3. **Assessment Workflow**: Assign Assessment → Send Invitation → Monitor Completion → Score Results
4. **Candidate Evaluation**: Review All Data → Generate Match Score → Recommend Action

See [workflows.md](./workflows.md) for detailed workflow sequences.

## External Dependencies

| Service | Direction | Purpose |
|---------|-----------|---------|
| Candidate Domain | Consumes | Retrieve candidate profile information |
| Job Domain | Consumes | Retrieve job requirements for matching |
| Communications Domain | Produces | Send notifications and outreach messages |
| Recruitment Pipeline Domain | Produces/Consumes | Update candidate pipeline stage |
| Azure Form Recognizer | Consumes | Enhanced document parsing |
| Azure OpenAI Service | Consumes | Semantic analysis of skills and experiences |

## API Documentation

- REST API: [openapi.yaml](../api/openapi.yaml)
- WebSocket API: [asyncapi.yaml](../api/asyncapi.yaml)

## Event Production and Consumption

### Events Published
- `ResumeProcessingCompleted`: When a candidate's resume has been fully parsed and analyzed
- `CandidateSkillsMatched`: When candidate skills have been matched to a job
- `InterestCheckSent`: When an interest check has been initiated
- `CandidateInterested`: When a candidate responds positively to interest check
- `CandidateNotInterested`: When a candidate declines further consideration
- `AssessmentAssigned`: When a candidate is assigned an assessment
- `AssessmentCompleted`: When a candidate completes an assessment
- `CandidateQualified`: When a candidate passes screening criteria
- `CandidateDisqualified`: When a candidate fails screening criteria
- `CandidateDiscoveryStarted`: When light screening begins for a job
- `CandidateDiscoveryCompleted`: When light screening finishes finding candidates
- `CandidateProfileGenerated`: When a candidate profile is created from scraped data

### Events Consumed
- `JobCreated`: When a new job is created (to prepare matching capability)
- `CandidateApplied`: When a candidate applies for a job (to trigger screening)
- `InterestCheckResponseReceived`: When a communication response is received
- `CandidateStageUpdated`: When a candidate's pipeline stage changes
- `CandidateReadyForScreening`: When the pipeline indicates a candidate is ready for screening
