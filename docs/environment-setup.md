# Environment Setup Guide

This document explains how to securely set up environment variables for local development.

## Overview

For security reasons, environment variables containing sensitive information (like API keys and secrets) are not stored in the repository. Instead, we use:

- `.env.example` files that define the required variables but with placeholder values
- A secure Azure Key Vault to store actual development secrets
- A setup script that fetches secrets and creates `.env` files

## Prerequisites

1. Install the Azure CLI:
   - [Azure CLI Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)

2. Log in to Azure:
   ```bash
   az login
   ```

3. Ensure you have access to the development Key Vault:
   - Contact the DevOps team if you need access to the `cognitivehire-dev-kv` vault

4. Install Node.js and npm:
   - [Node.js Download](https://nodejs.org/en/download/) (LTS version recommended)
   - Verify installation with:
     ```bash
     node --version
     npm --version
     ```

5. Install Frontend Dependencies:
   ```bash
   # Navigate to the frontend directory
   cd frontend
   
   # Install Next.js
   npm install next
   
   # Install Node types
   npm i --save-dev @types/node
   
   # Install React and TypeScript types
   npm install react react-dom @types/react @types/react-dom
   
   # Install Material UI
   npm install @mui/material @emotion/react @emotion/styled
   
   # Install Material UI Icons
   npm install @mui/icons-material
   
   # Install Azure AD B2C Authentication
   npm install @azure/msal-browser
   # If you're using yarn, run: yarn add @azure/msal-browser
   
   # Install all other dependencies from package.json
   npm install
   ```

## Setting Up Environment Variables

### Automatic Setup (Recommended)

Run the setup script to fetch secrets and create `.env` files:

```bash
# From the project root
python scripts/setup-env.py --service recruitment
```

This will create the `.env` file for the recruitment service using secrets from Azure Key Vault.

Repeat for other services as needed:

```bash
python scripts/setup-env.py --service candidate
```

### Manual Setup (Alternative)

If you prefer to set up environment variables manually or don't have access to the Key Vault:

1. Copy the `.env.example` file to `.env`:
   ```bash
   cp backend/recruitment-service/.env.example backend/recruitment-service/.env
   ```

2. Contact the development lead to get the required secret values

3. Edit the `.env` file and replace placeholder values with actual secrets

## Environment Variables in CI/CD

In CI/CD pipelines, environment variables are injected automatically from:

- GitHub Secrets (for GitHub Actions)
- Azure DevOps Variable Groups (for Azure Pipelines)

## Managing Secrets

If you need to update or add new secrets:

1. For development secrets:
   - Update the Azure Key Vault using the Azure Portal or CLI
   - Update the `setup-env.py` script if needed

2. For CI/CD secrets:
   - Update the appropriate secrets in GitHub or Azure DevOps
   - Update pipeline definitions if needed

## Security Best Practices

- Never commit `.env` files or actual secrets to the repository
- Don't log environment variables containing secrets
- Rotate secrets regularly according to the security policy
- Use different secrets for development, testing, and production

<!-- In environment-setup.md -->
> **Next steps**: After setting up your environment, see the [Development Guide](development-guide.md) for coding standards and workflows.
