# Key Workflows

This document outlines the primary workflows implemented by the Screening Service.

## Resume Upload and Parsing Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant RM as Resume Manager
    participant RP as Resume Parser
    participant FR as Azure Form Recognizer
    participant AI as Azure OpenAI
    participant DB as PostgreSQL
    participant BS as Blob Storage
    participant WS as WebSocket

    Client->>API: POST /resumes (file, candidate_id)
    API->>RM: Upload Resume
    RM->>BS: Store Document
    BS-->>RM: Document URL
    RM->>DB: Create Resume Record
    DB-->>RM: Resume ID
    RM-->>API: Resume Created Response
    API-->>Client: 201 Created (Resume ID)
    
    Client->>API: POST /resumes/{id}/parse
    API->>RM: Parse Resume Request
    RM->>RP: Process Resume
    RP->>WS: Notify Parsing Started
    WS-->>Client: {event: parsing_started}
    RP->>BS: Download Document
    BS-->>RP: Document Content
    
    Note over RP: Try Text Parser First (Tier 1)
    RP->>RP: Extract with Text Parser
    
    alt Text Parser Success
        RP->>DB: Store Parsed Data
    else Text Parser Failed or Low Confidence
        Note over RP: Try Form Recognizer (Tier 2)
        RP->>FR: Extract Text & Structure
        FR-->>RP: Extracted Content
        
        alt Form Recognizer Success
            RP->>DB: Store Parsed Data
        else Form Recognizer Failed or Low Confidence
            Note over RP: Try Vision AI (Tier 3)
            RP->>AI: Process Document Image
            AI-->>RP: Vision Analysis Results
            RP->>DB: Store Parsed Data
        end
    end
    
    RP->>WS: Notify Progress
    WS-->>Client: {event: progress, percentage: 50}
    RP->>AI: Analyze Skills & Experience
    AI-->>RP: Enhanced Structured Data
    RP->>DB: Store Parsed Data
    DB-->>RP: Success
    RP->>WS: Notify Parsing Completed
    WS-->>Client: {event: parsing_completed}
    RP-->>RM: Parsing Completed
    RM-->>API: Success Response
    API-->>Client: 200 OK
```

## Interest Check Workflow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant ICM as Interest Check Manager
    participant CD as Candidate Domain
    participant JD as Job Domain
    participant CM as Communications Domain
    participant DB as PostgreSQL
    participant WS as WebSocket
    participant Candidate

    Client->>API: POST /interest-checks (candidate_id, job_id, channel)
    API->>ICM: Create Interest Check
    ICM->>CD: Get Candidate Details
    CD-->>ICM: Candidate Details
    ICM->>JD: Get Job Details
    JD-->>ICM: Job Details
    ICM->>DB: Create Interest Check Record
    DB-->>ICM: Interest Check ID
    ICM-->>API: Interest Check Created Response
    API-->>Client: 201 Created (Interest Check ID)
    
    Client->>API: POST /interest-checks/{id}/send
    API->>ICM: Send Interest Check
    ICM->>DB: Update Status to Sending
    ICM->>WS: Notify Interest Check Sending
    WS-->>Client: {event: sending}
    
    alt Email Channel
        ICM->>CM: Send Email
        CM-->>ICM: Email Sent
    else SMS Channel
        ICM->>CM: Send SMS
        CM-->>ICM: SMS Sent
    else Call Channel
        ICM->>CM: Schedule Call
        CM-->>ICM: Call Scheduled
    else LinkedIn Channel
        ICM->>CM: Send LinkedIn Message
        CM-->>ICM: Message Sent
    end
    
    ICM->>DB: Update Status to Sent
    ICM->>WS: Notify Interest Check Sent
    WS-->>Client: {event: sent}
    ICM-->>API: Success Response
    API-->>Client: 200 OK
    
    alt Candidate Responds
        Candidate->>CM: Response (Email/SMS/Call)
        CM->>ICM: Forward Response
        ICM->>DB: Store Response & Update Status
        ICM->>WS: Notify Response Received
        WS-->>Client: {event: response_received, status: interested/not_interested}
    else No Response Timeout
        ICM->>DB: Update Status to No Response
        ICM->>WS: Notify No Response
        WS-->>Client: {event: timeout, status: no_response}
    end
```

## Skills Matching Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant SM as Skills Matcher
    participant JD as Job Domain
    participant CD as Candidate Domain
    participant AI as Azure OpenAI
    participant DB as PostgreSQL
    participant WS as WebSocket

    Client->>API: POST /jobs/{id}/match (candidate_ids, matching_type)
    API->>SM: Match Candidates to Job
    SM->>JD: Get Job Requirements
    JD-->>SM: Job Requirements
    SM->>WS: Notify Matching Started
    WS-->>Client: {event: matching_started}
    
    loop For Each Candidate
        SM->>CD: Get Candidate Skills
        CD-->>SM: Candidate Skills
        
        alt Keyword Matching
            SM->>SM: Perform Keyword Matching
        else Semantic Matching
            SM->>AI: Generate Embeddings
            AI-->>SM: Skill Embeddings
            SM->>SM: Calculate Semantic Similarity
        else Hybrid Matching
            SM->>SM: Perform Keyword Matching
            SM->>AI: Generate Embeddings
            AI-->>SM: Skill Embeddings
            SM->>SM: Calculate Combined Score
        end
        
        SM->>DB: Store Match Results
        SM->>WS: Notify Candidate Matched
        WS-->>Client: {event: candidate_matched, candidate_id: X, score: Y}
    end
    
    SM->>DB: Finalize Match Results
    SM->>WS: Notify Matching Completed
    WS-->>Client: {event: matching_completed}
    SM-->>API: Matching Results
    API-->>Client: 200 OK (Match Results)
```

## Assessment Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant AM as Assessment Manager
    participant CD as Candidate Domain
    participant CM as Communications Domain
    participant AP as Assessment Provider
    participant DB as PostgreSQL
    participant WS as WebSocket
    participant Candidate

    Client->>API: POST /assessments (candidate_id, job_id, assessment_type_id)
    API->>AM: Create Assessment
    AM->>CD: Get Candidate Details
    CD-->>AM: Candidate Details
    AM->>DB: Create Assessment Record
    AM->>AP: Create Assessment in Provider
    AP-->>AM: External Assessment ID & Access URL
    AM->>DB: Store External Details
    AM-->>API: Assessment Created Response
    API-->>Client: 201 Created (Assessment ID)
    
    Client->>API: POST /assessments/{id}/send
    API->>AM: Send Assessment Invitation
    AM->>CM: Send Email Invitation with Link
    CM-->>AM: Email Sent
    AM->>DB: Update Status to Invited
    AM->>WS: Notify Assessment Invited
    WS-->>Client: {event: invited}
    AM-->>API: Success Response
    API-->>Client: 200 OK
    
    Candidate->>AP: Access Assessment Portal
    AP->>AM: Notify Assessment Started (Webhook)
    AM->>DB: Update Status to Started
    AM->>WS: Notify Assessment Started
    WS-->>Client: {event: started}
    
    loop During Assessment
        Candidate->>AP: Submit Answers
        AP->>AM: Progress Update (Webhook)
        AM->>DB: Update Progress
        AM->>WS: Notify Assessment Progress
        WS-->>Client: {event: in_progress, progress: X%}
    end
    
    Candidate->>AP: Complete Assessment
    AP->>AM: Notify Assessment Completed with Results (Webhook)
    AM->>DB: Update Status to Completed
    AM->>DB: Store Score
    AM->>WS: Notify Assessment Completed
    WS-->>Client: {event: completed, score: X}
```

## Light Screening Workflow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant CDS as Candidate Discovery Service
    participant SD as Sourcing Domain
    participant SM as Skills Matcher
    participant AI as Azure OpenAI
    participant DB as PostgreSQL
    participant WS as WebSocket

    Client->>API: POST /jobs/{id}/discover-candidates (search_criteria)
    API->>CDS: Discover Candidates Request
    CDS->>WS: Notify Discovery Started
    WS-->>Client: {event: discovery_started}
    
    CDS->>SD: Get Job Requirements
    SD-->>CDS: Job Requirements
    
    CDS->>AI: Generate Search Queries
    AI-->>CDS: Optimized Search Queries
    
    loop For Each Search Query
        CDS->>SD: Search Candidates (query)
        SD-->>CDS: Candidate Search Results
        CDS->>WS: Notify Progress
        WS-->>Client: {event: progress, found: X}
    end
    
    CDS->>DB: Store Candidate References
    CDS->>DB: Store Scraped Data
    
    CDS->>SM: Perform Light Skills Matching
    SM->>AI: Analyze Skills from Scraped Data
    AI-->>SM: Extracted Skills
    SM->>DB: Store Match Results
    
    CDS->>WS: Notify Discovery Completed
    WS-->>Client: {event: discovery_completed, candidates_found: X}
    CDS-->>API: Discovery Results
    API-->>Client: 200 OK (Discovery Results)
```

## Screening Type Decision Flow

```mermaid
sequenceDiagram
    participant Client
    participant API as API Gateway
    participant CEF as Candidate Evaluation Framework
    participant CD as Candidate Domain
    participant JD as Job Domain
    participant DB as PostgreSQL

    Client->>API: POST /screenings/determine-type (candidate_id, job_id)
    API->>CEF: Evaluate Candidate Request
    
    CEF->>CD: Get Candidate Details
    CD-->>CEF: Candidate Details
    
    CEF->>JD: Get Job Details
    JD-->>CEF: Job Details
    
    Note over CEF: Determine Screening Type
    
    alt Candidate has resume AND subscription allows deep screening
        CEF->>CEF: Select Deep Screening
        CEF->>DB: Record Screening Type = DEEP
    else No resume OR limited subscription
        CEF->>CEF: Select Light Screening
        CEF->>DB: Record Screening Type = LIGHT
    end
    
    CEF-->>API: Screening Type Decision
    API-->>Client: 200 OK (Screening Type)
```
