const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const glob = require('glob');

/**
 * Generate an updated API index by scanning all OpenAPI/AsyncAPI specs
 * and extracting their metadata.
 */
async function generateApiIndex() {
  // Find all API specs
  const openApiSpecs = glob.sync('backend/*/api/openapi.yaml');
  const asyncApiSpecs = glob.sync('backend/*/api/asyncapi.yaml');
  
  // Create service table rows
  const serviceTableRows = openApiSpecs.map(specPath => {
    try {
      const content = fs.readFileSync(specPath, 'utf8');
      const spec = yaml.load(content);
      const serviceName = specPath.split('/')[1].replace('-service', '');
      
      return {
        service: spec.info.title || serviceName,
        description: spec.info.description?.split('\n')[0] || 'No description',
        version: spec.info.version || 'Unknown',
        specPath: specPath,
        servicePath: serviceName
      };
    } catch (error) {
      console.error(`Error processing ${specPath}: ${error}`);
      return null;
    }
  }).filter(Boolean);
  
  // Create realtime table rows
  const realtimeTableRows = asyncApiSpecs.map(specPath => {
    try {
      const content = fs.readFileSync(specPath, 'utf8');
      const spec = yaml.load(content);
      const serviceName = specPath.split('/')[1].replace('-service', '');
      
      return {
        service: spec.info.title || serviceName,
        description: spec.info.description?.split('\n')[0] || 'No description',
        version: spec.info.version || 'Unknown',
        specPath: specPath,
        servicePath: serviceName
      };
    } catch (error) {
      console.error(`Error processing ${specPath}: ${error}`);
      return null;
    }
  }).filter(Boolean);
  
  // Generate markdown
  const template = `
# Cognitive Hire API Reference

This document provides an automatically generated index of all API specifications and documentation across the Cognitive Hire platform.

> Last updated: ${new Date().toISOString().split('T')[0]}

## REST APIs

| Service | Description | Version | Documentation |
|---------|-------------|---------|---------------|
${serviceTableRows.map(row => 
  `| ${row.service} | ${row.description} | ${row.version} | [OpenAPI](../backend/${row.servicePath}/api/openapi.yaml) \| [HTML](./services/${row.servicePath}/index.html) |`
).join('\n')}

## Real-time APIs

| Service | Description | Version | Documentation |
|---------|-------------|---------|---------------|
${realtimeTableRows.map(row => 
  `| ${row.service} | ${row.description} | ${row.version} | [AsyncAPI](../backend/${row.servicePath}/api/asyncapi.yaml) |`
).join('\n')}

## Authentication

All API requests require authentication through JWT tokens. See the [Authentication Guide](./authentication.md) for details.

## API Clients

- [TypeScript](https://github.com/example/cognitivehire-ts) 
- [Python](https://github.com/example/cognitivehire-python)

## Additional Resources

- [Getting Started](./api-getting-started.md)
- [Error Handling](./error-handling.md)
- [Webhooks](./webhooks.md)
- [Rate Limits](./rate-limits.md)
`;

  // Write the generated content
  fs.writeFileSync('docs/api/index.md', template);
  console.log('API index generated successfully');
}

generateApiIndex().catch(console.error);
