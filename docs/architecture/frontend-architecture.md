# Cognitive Hire Frontend Architecture

## Overview

The frontend architecture for Cognitive Hire consists of three Next.js applications built on a shared component library and unified design system. This document outlines the technical approach, structure, and implementation details.

## Applications

| Application | Purpose | Users | Key Features |
|-------------|---------|-------|--------------|
| Main Platform | Primary recruitment interface | Recruiters, Hiring Managers | Job management, Candidate pipeline, Interview scheduling |
| Mobile Experience | On-the-go accessibility | Hiring Managers, Interviewers | Candidate review, Interview feedback, Approvals |
| Admin Portal | System administration | Admins, Support | User management, Configuration, Analytics |

## Technology Stack

### Core Technologies

- **Next.js 14+**: React framework with App Router architecture
- **TypeScript**: Type-safe JavaScript for better maintainability
- **Redux Toolkit**: For centralized state management
- **React Query**: For server state management and data synchronization
- **Material UI**: Component library and design system

### Supporting Libraries

- **Formik + Yup**: Form management and validation
- **date-fns**: Date manipulation and formatting
- **i18next**: Internationalization
- **recharts**: Data visualization
- **react-virtualized**: Performance optimization for large lists
- **socket.io-client**: WebSocket communication with backend
- **next-pwa**: Progressive Web App capabilities

## Architecture Patterns

### Next.js App Router Structure

```
/app                      # Next.js App Router structure
  /layout.tsx             # Root layout with common UI
  /page.tsx               # Landing page
  /(auth)                 # Auth routes group 
    /login/page.tsx       # Login page
    /register/page.tsx    # Registration page
  /(dashboard)            # Dashboard routes group
    /layout.tsx           # Dashboard layout
    /page.tsx             # Dashboard home
    /jobs/                # Job management
      /page.tsx           # Jobs listing
      /[id]/page.tsx      # Job details
      /new/page.tsx       # Create new job
    /candidates/          # Candidate management
    /interviews/          # Interview scheduling
  /api                    # API routes
    /auth/[...nextauth]/route.ts  # Authentication API
    /jobs/route.ts        # Jobs API endpoints
    /webhooks/route.ts    # Webhook handlers

/components               # Reusable components
  /ui                     # Basic UI components
  /features               # Feature-specific components

/lib                      # Shared utilities
  /api                    # API client 
  /hooks                  # Custom hooks
  /types                  # TypeScript types
  /utils                  # Helper functions

/public                   # Static assets
```

### Next.js-specific Architecture Elements

1. **Server vs. Client Components**:

   ```typescript
   // Server Component (default in App Router)
   // /app/jobs/page.tsx
   import { getJobs } from '@/lib/api/jobs';
   
   export default async function JobsPage() {
     // Data fetching happens on the server
     const jobs = await getJobs();
     
     return (
       <div>
         <h1>Jobs</h1>
         <JobList jobs={jobs} />
       </div>
     );
   }
   ```

   ```typescript
   // Client Component (explicit)
   // /components/features/jobs/JobFilterForm.tsx
   'use client';
   
   import { useState } from 'react';
   
   export default function JobFilterForm({ onFilter }) {
     const [filters, setFilters] = useState({});
     
     return (
       <form onSubmit={() => onFilter(filters)}>
         {/* Form content */}
       </form>
     );
   }
   ```

2. **Data Fetching Approaches**:

   ```typescript
   // Server Component data fetching
   async function JobDetails({ params }) {
     const job = await getJobById(params.id);
     return <JobDetailView job={job} />;
   }
   
   // Client Component data fetching with React Query
   'use client';
   
   function JobApplications({ jobId }) {
     const { data, isLoading } = useQuery(['applications', jobId], 
       () => getApplications(jobId)
     );
     
     if (isLoading) return <Spinner />;
     return <ApplicationList data={data} />;
   }
   ```

3. **Route Handlers (API Routes)**:

   ```typescript
   // /app/api/jobs/route.ts
   import { NextResponse } from 'next/server';
   
   export async function GET(request) {
     const jobs = await fetchJobsFromBackend();
     return NextResponse.json(jobs);
   }
   
   export async function POST(request) {
     const data = await request.json();
     const result = await createJobInBackend(data);
     return NextResponse.json(result);
   }
   ```

### State Management Strategy

We use a hybrid state management approach:

1. **Redux**: For global application state
   - User authentication status
   - UI preferences and settings
   - Cross-cutting concerns

2. **React Query**: For server state
   - Client-side API data fetching and caching
   - Automatic re-fetching and synchronization
   - Loading and error states

3. **Server Component State**: For server-rendered data
   - Initial page data
   - SEO-critical content
   - Non-interactive content

4. **React Context**: For feature-specific shared state
   - Theme context
   - Notification context
   - Feature flags

5. **Local State**: For component-specific state
   - Form input values
   - UI toggling states
   - Ephemeral UI state

### API Integration

#### REST API Integration

The application uses a combination of server-side data fetching and React Query:

```typescript
// Server-side in page.tsx
async function JobsPage({ searchParams }) {
  // Server-side data fetching
  const jobs = await getJobs(searchParams);
  
  return (
    <div>
      <JobsHeader />
      <ClientJobsContainer initialData={jobs} />
    </div>
  );
}

// Client-side component
'use client';

function ClientJobsContainer({ initialData }) {
  const [filters, setFilters] = useState({});
  
  // Client-side data fetching with React Query
  const { data, isLoading } = useQuery(
    ['jobs', filters], 
    () => getJobs(filters),
    { initialData } // Use server-fetched data initially
  );
  
  return (
    <>
      <JobFilters onChange={setFilters} />
      <JobList data={data} isLoading={isLoading} />
    </>
  );
}
```

#### WebSocket Integration

For real-time updates, we use a custom WebSocket hook in client components:

```typescript
// WebSocket hook in client component
'use client';

function useCandidatePipelineUpdates(jobId) {
  const [updates, setUpdates] = useState([]);
  
  useWebSocketSubscription({
    channel: `job:${jobId}:candidates`,
    onMessage: (message) => {
      setUpdates(prev => [...prev, message]);
    }
  });
  
  return updates;
}

// Usage in a client component
function CandidatePipeline({ jobId }) {
  const updates = useCandidatePipelineUpdates(jobId);
  
  return (
    <div>
      <PipelineView />
      <ActivityFeed updates={updates} />
    </div>
  );
}
```

### Styling Approach

The application uses Material UI with CSS Modules for component-specific styling:

```typescript
// Global theme configuration
// /app/theme.ts
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    primary: {
      main: '#3069f0',
    },
    // ...other settings
  },
});

// Component-specific styling with CSS Modules
// /components/features/jobs/JobCard/JobCard.module.css
.cardContainer {
  margin-bottom: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.cardContainer:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

// Component with styling
// /components/features/jobs/JobCard/JobCard.tsx
'use client';

import { Card, CardContent } from '@mui/material';
import styles from './JobCard.module.css';

export function JobCard({ job }) {
  return (
    <Card className={styles.cardContainer}>
      <CardContent>
        <h3>{job.title}</h3>
        <p>{job.location}</p>
      </CardContent>
    </Card>
  );
}
```

## Next.js Performance Benefits

### Server Components

- Reduced client-side JavaScript bundle
- Faster page loads and improved SEO
- More efficient data fetching directly from backends
- Example: Our job listings use server components for initial render

### Image Optimization

```typescript
// Optimized images with Next.js Image component
import Image from 'next/image';

function CompanyLogo({ company }) {
  return (
    <Image
      src={company.logoUrl}
      alt={`${company.name} logo`}
      width={200}
      height={100}
      placeholder="blur"
      blurDataURL={company.logoPlaceholder}
      priority={true}
    />
  );
}
```

### Routing Optimizations

- Automatic code splitting by route
- Prefetching for faster navigation
- Parallel route loading for complex layouts

### Static and Dynamic Rendering

- Static generation (SSG) for public pages
- Server-side rendering (SSR) for personalized content
- Incremental Static Regeneration (ISR) for content that changes infrequently

```typescript
// Static generation with revalidation
export async function generateStaticParams() {
  const jobs = await getPopularJobs();
  return jobs.map(job => ({ id: job.id }));
}

// Revalidation period
export const revalidate = 3600; // Revalidate every hour
```

## Testing Strategy

### Testing Levels

1. **Unit Tests**:
   - Jest for test running
   - React Testing Library for component testing
   - Mock Service Worker for API mocking

2. **Component Tests**:
   - Storybook for component documentation and visual testing
   - Component stories as living documentation

3. **Integration Tests**:
   - Testing feature workflows
   - Testing interactions between components

4. **End-to-End Tests**:
   - Playwright for comprehensive cross-browser testing
   - Testing complete workflows across applications
   - API testing alongside UI verification

### Testing Example

```typescript
// Server component test
import { render, screen } from '@testing-library/react';
import { getJobById } from '@/lib/api/jobs';
import JobPage from '@/app/jobs/[id]/page';

// Mock API module
jest.mock('@/lib/api/jobs', () => ({
  getJobById: jest.fn()
}));

describe('Job Page', () => {
  it('displays job details', async () => {
    getJobById.mockResolvedValue({
      id: '123',
      title: 'Senior Engineer',
      location: 'Remote'
    });

    await JobPage({ params: { id: '123' } });
    
    expect(screen.getByRole('heading')).toHaveTextContent('Senior Engineer');
    expect(screen.getByText('Remote')).toBeInTheDocument();
  });
});

// Client component test with Playwright
import { test, expect } from '@playwright/test';

test('user can apply for job', async ({ page }) => {
  // Log in first
  await page.goto('/login');
  await page.fill('[data-testid="email"]', 'user@example.com');
  await page.fill('[data-testid="password"]', 'password');
  await page.click('button[type="submit"]');
  
  // Navigate to job
  await page.goto('/jobs/software-engineer');
  
  // Verify job details are visible
  await expect(page.locator('h1')).toContainText('Software Engineer');
  
  // Apply for job
  await page.click('[data-testid="apply-button"]');
  
  // Fill application form
  await page.fill('[data-testid="cover-letter"]', 'I am interested in this position.');
  await page.click('[data-testid="submit-application"]');
  
  // Verify success message
  await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
});
```

## Deployment and CI/CD

### Build Process

1. **Environment Configuration**:
   - Environment variables for different environments
   - Configuration validation at build time

2. **Build Stages**:
   - Linting and type checking
   - Running unit and integration tests
   - Building Next.js application
   - Static export (when applicable)

3. **Optimization**:
   - Bundle analysis
   - Image optimization
   - Font optimization

### Deployment Options

1. **Azure Static Web Apps** (Primary option):
   - First-class support for Next.js applications
   - Global CDN with edge caching
   - Managed authentication integration
   - GitHub Actions integration
   - Preview environments for PRs

2. **Containerized Deployment** (For special cases):
   - Docker container with Next.js app
   - Deployed to Azure Container Apps
   - Custom configuration options

### CI/CD Pipeline with GitHub Actions

```yaml
name: Frontend CI/CD

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Lint
        run: npm run lint
        
      - name: Type check
        run: npm run type-check
        
      - name: Test
        run: npm run test
        
      - name: Build
        run: npm run build
        
      - name: Deploy to Azure Static Web Apps
        if: github.ref == 'refs/heads/main'
        uses: Azure/static-web-apps-deploy@v1
        with:
          azure_static_web_apps_api_token: ${{ secrets.AZURE_STATIC_WEB_APPS_API_TOKEN }}
          repo_token: ${{ secrets.GITHUB_TOKEN }}
          action: "upload"
          app_location: "/" 
          api_location: "/api"
          output_location: ".next"
```

## Monitoring and Analytics

- **Azure Application Insights** for:
  - Core Web Vitals monitoring
  - Error tracking
  - User behavior analytics
  - Performance monitoring

## Accessibility and Internationalization

- WCAG 2.1 AA compliance
- Built-in internationalization with Next.js i18n
- RTL support via Material UI
- Keyboard navigation throughout
- Screen reader compatibility

## Progressive Web App Features

Next.js with next-pwa provides:

- Offline support for key features
- Push notifications
- Add to home screen capability
- Background sync for offline actions
- Precaching of critical resources
