# Authentication Guide

## Overview

Cognitive Hire uses Azure AD B2C as the central authentication provider for both frontend and backend systems. This provides:

- Unified login experience across all applications
- Support for social logins (Microsoft, Google)
- Enterprise-grade security and compliance
- Seamless integration with Azure services

## Architecture

Our authentication architecture follows these principles:

1. **Single Authentication Provider**: Azure AD B2C handles all authentication
2. **Token-Based Flow**:
   - Users authenticate through the frontend directly with Azure AD B2C
   - Azure AD B2C issues access and ID tokens
   - Frontend securely stores tokens
   - Backend validates tokens independently

![Authentication Flow](./images/auth-flow.png)

## Setup Instructions

### Prerequisites

1. An Azure subscription
2. Azure AD B2C tenant configured with:
   - Microsoft and Google identity providers
   - User flows for sign-in/sign-up
   - Application registration for our API and frontend

### Backend Configuration

1. Set environment variables in your `.env` file:

