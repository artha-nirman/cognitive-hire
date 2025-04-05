# Cognitive Hire Platform Cost Estimate

This document provides a monthly cost estimate for the Cognitive Hire platform based on the following usage parameters:
- 25 job postings per month
- 1,000 resumes sourced per job (25,000 total)
- 50 applications submitted per job (1,250 total)

## Cost Breakdown by Category

### 1. Compute Resources

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Azure Container Apps | 14 microservices with scale-to-zero, avg 2 CPU cores/4GB RAM | $350-450 |
| Azure Functions | Event processing, background tasks (~100K executions) | $15-30 |
| **Subtotal** | | **$365-480** |

### 2. AI & Cognitive Services

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Azure OpenAI (GPT-4) | Job description creation (25 jobs × 5K tokens) | $12-15 |
| Azure OpenAI (GPT-3.5) | Screening (1,250 applications × 10K tokens) | $25-30 |
| Azure OpenAI (GPT-3.5) | Sourcing queries (25 jobs × 5K tokens) | $3-5 |
| Azure Form Recognizer | Resume parsing (25,000 resumes) | $1,250* |
| Azure Cognitive Search | Vector embeddings for 25,000 resumes | $150-200 |
| **Subtotal** | | **$1,440-1,500** |
\* *Form Recognizer costs can be optimized by implementing custom extraction*

### 3. Data Storage

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| PostgreSQL | Standard tier (8 vCores) | $400-450 |
| Cosmos DB | Provisioned throughput (400 RU/s) | $175-225 |
| Blob Storage | Resume storage (~12.5GB new + historical) | $10-15 |
| **Subtotal** | | **$585-690** |

### 4. Messaging & Integration

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Event Grid | ~50K events per month | $9 |
| Service Bus | Standard tier | $10 |
| **Subtotal** | | **$19** |

### 5. DevOps & Monitoring

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| GitHub Actions | 3,000 minutes/month | $36 |
| Azure Container Registry | Basic tier | $5 |
| Application Insights | Monitoring, ~50GB data | $150 |
| Key Vault | Standard tier | $5 |
| **Subtotal** | | **$196** |

### 6. Security & Networking

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Azure AD B2C | ~500 users, ~10K authentications | $25-35 |
| API Management | Developer tier | $49 |
| Front Door | Standard tier | $37 |
| **Subtotal** | | **$111-121** |

### 7. Communications

| Service | Usage | Monthly Cost |
|---------|-------|--------------|
| Azure Communication Services | Emails (~5,000) | $10 |
| Azure Communication Services | SMS notifications (~1,000) | $20 |
| Azure Communication Services | Voice calls (~250) | $25 |
| **Subtotal** | | **$55** |

### 8. Frontend Infrastructure

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Azure Static Web Apps | Standard tier (3 apps) | $27-39 |
| Azure CDN | Standard Microsoft tier (500GB bandwidth) | $35-50 |
| Content storage | Static assets and cached data | $5-10 |
| **Subtotal** | | **$67-99** |

### 9. Frontend Development Tools

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| Storybook (Optional) | Chromatic service (10K snapshots) | $0-149* |
| LogRocket (Optional) | Starter plan (10K sessions) | $0-99* |
| **Subtotal** | | **$0-248*** |
\* *Optional services can start with free tier and scale as needed*

## Updated Total Monthly Operating Cost

| Category | Cost Range |
|----------|------------|
| Compute Resources | $365-480 |
| AI & Cognitive Services | $1,440-1,500 |
| Data Storage | $585-690 |
| Messaging & Integration | $19 |
| DevOps & Monitoring | $196 |
| Security & Networking | $111-121 |
| Communications | $55 |
| Frontend Infrastructure | $67-99 |
| Frontend Development Tools | $0-248* |
| **Monthly Total** | **$2,840-3,408** |
\* *Including optional development tools*

## Cost Optimization Recommendations

### 1. Form Recognizer Optimization

The most significant cost driver is Azure Form Recognizer for parsing 25,000 resumes monthly ($1,250). Consider these alternatives:

- **Pre-process with custom OCR**: Reduce Form Recognizer usage by 80%
- **Batch processing**: Implement a custom resume parser for standard formats
- **Progressive extraction**: Only use advanced parsing for candidates that pass initial screening

This could reduce costs to $250-400/month.

### 2. Compute Resource Optimization

With high volume processing:

- Implement efficient autoscaling for Container Apps
- Create serverless functions for batch processing
- Optimize idle container shutdown to minimize running costs
- Consider reserved instances for baseline capacity

### 3. Database Tier Optimization

- Implement efficient database queries
- Use caching aggressively to reduce database load
- Consider read replicas only where absolutely necessary
- Use time-based partitioning for historical data

### 4. Storage Optimization

- Compress resumes before storage
- Implement tiered storage for older resumes
- Set lifecycle policies to archive older data automatically

### 5. Monitoring Configuration

- Set custom retention policies for different log types
- Implement sampling for high-volume telemetry
- Focus detailed logging on critical paths only

### 6. Frontend Optimization

- **Next.js-specific Optimizations**:
  - Use Incremental Static Regeneration for semi-dynamic content
  - Implement image optimization with next/image
  - Leverage React Server Components to reduce JS payload
  - Configure appropriate caching strategies per route

- **JavaScript Optimization**:
  - Take advantage of automatic code splitting in Next.js
  - Keep client components lean
  - Reduce client-side JavaScript with server components

- **Hosting Optimization**:
  - Configure Azure Static Web Apps regions closest to user base
  - Implement A/B testing pattern with minimal overhead
  - Use Azure CDN effectively for global asset delivery
  - Configure appropriate revalidation periods in Next.js

These optimizations should maintain or improve frontend costs compared to the previous approach.

## Additional Considerations

1. **Scaling Costs**: At 50 jobs/month, expect costs to increase to approximately $4,500-5,200/month
2. **Initial Setup Costs**: One-time costs for development, environment setup, and initial training
3. **AI Model Training**: Budget for any custom model training required
4. **Data Transfer**: Costs may increase with significant external data transfers

## ROI Analysis

At 25 jobs/month with 50 applicants each:
- Traditional recruitment cost: ~$5,000-7,500/month (manual screening, sourcing)
- Time-to-hire reduction: 30-50% faster placement
- Quality improvement: Better candidate matches through consistent AI screening
- Scalability: System can handle 2-3x volume with minimal additional cost
