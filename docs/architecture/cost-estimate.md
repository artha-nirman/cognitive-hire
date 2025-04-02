# Cognitive Hire Platform Cost Estimate

This document provides a monthly cost estimate for the Cognitive Hire platform based on the following usage parameters:

## Interactive Cost Calculator

<div id="costCalculator" style="border: 1px solid #ddd; padding: 20px; border-radius: 5px; background-color: #f9f9f9; margin: 20px 0;">
  <h3>Input Parameters</h3>
  <div style="display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 20px;">
    <div>
      <label for="jobCount">Number of job postings per month:</label>
      <input type="number" id="jobCount" value="25" min="1" style="width: 100px; margin-left: 10px;">
    </div>
    <div>
      <label for="resumesPerJob">Resumes sourced per job:</label>
      <input type="number" id="resumesPerJob" value="1000" min="1" style="width: 100px; margin-left: 10px;">
    </div>
    <div>
      <label for="applicationsPerJob">Applications per job:</label>
      <input type="number" id="applicationsPerJob" value="50" min="1" style="width: 100px; margin-left: 10px;">
    </div>
  </div>

  <h3>Monthly Cost Breakdown</h3>
  <table id="costTable" style="width: 100%; border-collapse: collapse;">
    <thead>
      <tr style="background-color: #eee;">
        <th style="padding: 8px; text-align: left; border: 1px solid #ddd;">Category</th>
        <th style="padding: 8px; text-align: right; border: 1px solid #ddd;">Cost Range</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Compute Resources</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="compute">$365-480</span></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">AI & Cognitive Services</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="ai">$1,440-1,500</span></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Data Storage</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="storage">$585-690</span></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Messaging & Integration</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="messaging">$19</span></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">DevOps & Monitoring</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="devops">$196</span></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Security & Networking</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="security">$111-121</span></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Communications</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="communications">$55</span></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Frontend Infrastructure</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="frontend">$67-99</span></td>
      </tr>
      <tr>
        <td style="padding: 8px; border: 1px solid #ddd;">Frontend Development Tools</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="tools">$0-248</span></td>
      </tr>
      <tr style="font-weight: bold; background-color: #eee;">
        <td style="padding: 8px; border: 1px solid #ddd;">Monthly Total</td>
        <td style="padding: 8px; text-align: right; border: 1px solid #ddd;"><span id="total">$2,840-3,408</span></td>
      </tr>
    </tbody>
  </table>
  
  <p style="margin-top: 20px;"><em>Note: This calculator provides estimates based on the input parameters. Actual costs may vary.</em></p>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
  const inputs = ['jobCount', 'resumesPerJob', 'applicationsPerJob'];
  inputs.forEach(id => {
    document.getElementById(id).addEventListener('input', updateCosts);
  });

  function updateCosts() {
    const jobCount = parseInt(document.getElementById('jobCount').value) || 0;
    const resumesPerJob = parseInt(document.getElementById('resumesPerJob').value) || 0;
    const applicationsPerJob = parseInt(document.getElementById('applicationsPerJob').value) || 0;
    
    const totalResumes = jobCount * resumesPerJob;
    const totalApplications = jobCount * applicationsPerJob;
    
    // Compute resources: scales with overall workload
    const computeBase = 365;
    const computeMax = 480;
    const computeFactor = Math.min(1, (jobCount / 25) * 0.8 + (totalResumes / 25000) * 0.1 + (totalApplications / 1250) * 0.1);
    const compute = `$${Math.round(computeBase * computeFactor)}-${Math.round(computeMax * computeFactor)}`;
    
    // AI costs: scale directly with volume
    const aiBaseMin = 1440;
    const aiBaseMax = 1500;
    const aiFactor = (jobCount / 25) * 0.1 + (totalResumes / 25000) * 0.8 + (totalApplications / 1250) * 0.1;
    const ai = `$${Math.round(aiBaseMin * aiFactor)}-${Math.round(aiBaseMax * aiFactor)}`;
    
    // Storage costs: scales with total data volume (primarily resumes)
    const storageBase = 585;
    const storageMax = 690;
    const storageFactor = Math.min(1, (jobCount / 25) * 0.1 + (totalResumes / 25000) * 0.9);
    const storage = `$${Math.round(storageBase * storageFactor)}-${Math.round(storageMax * storageFactor)}`;
    
    // Some fixed costs with slight scaling
    const messagingBase = 19;
    const messagingFactor = Math.sqrt(jobCount / 25);
    const messaging = `$${Math.round(messagingBase * messagingFactor)}`;
    
    // Fixed costs for now
    const devops = "$196";
    const security = "$111-121";
    
    // Communications: scales with applications
    const commBase = 55;
    const commFactor = Math.sqrt(totalApplications / 1250);
    const communications = `$${Math.round(commBase * commFactor)}`;
    
    // Frontend costs
    const frontendMin = 67;
    const frontendMax = 99;
    const frontendFactor = Math.min(1, Math.sqrt(jobCount / 25));
    const frontend = `$${Math.round(frontendMin * frontendFactor)}-${Math.round(frontendMax * frontendFactor)}`;
    
    // Tools stay relatively constant
    const tools = "$0-248";
    
    // Update the UI
    document.getElementById('compute').textContent = compute;
    document.getElementById('ai').textContent = ai;
    document.getElementById('storage').textContent = storage;
    document.getElementById('messaging').textContent = messaging;
    document.getElementById('devops').textContent = devops;
    document.getElementById('security').textContent = security;
    document.getElementById('communications').textContent = communications;
    document.getElementById('frontend').textContent = frontend;
    document.getElementById('tools').textContent = tools;
    
    // Calculate total
    const min = Math.round(
      parseInt(compute.split('-')[0].replace('$', '')) + 
      parseInt(ai.split('-')[0].replace('$', '')) + 
      parseInt(storage.split('-')[0].replace('$', '')) + 
      parseInt(messaging.replace('$', '')) +
      parseInt(devops.replace('$', '')) +
      parseInt(security.split('-')[0].replace('$', '')) +
      parseInt(communications.replace('$', '')) +
      parseInt(frontend.split('-')[0].replace('$', ''))
    );
    
    const max = Math.round(
      parseInt(compute.split('-')[1]) + 
      parseInt(ai.split('-')[1].replace('$', '')) + 
      parseInt(storage.split('-')[1].replace('$', '')) + 
      parseInt(messaging.replace('$', '')) +
      parseInt(devops.replace('$', '')) +
      parseInt(security.split('-')[1].replace('$', '')) +
      parseInt(communications.replace('$', '')) +
      parseInt(frontend.split('-')[1].replace('$', '')) +
      248 // Max tools cost
    );
    
    document.getElementById('total').textContent = `$${min}-${max}`;
  }
});
</script>

## Static Cost Estimates

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
