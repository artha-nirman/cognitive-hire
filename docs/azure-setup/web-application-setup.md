# Setting Up Azure AD B2C for the Frontend Web Application

This guide provides step-by-step instructions for registering and configuring the frontend web application in Azure AD B2C.

## 1. Register the Web Application

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure AD B2C tenant
3. Select **App registrations** from the left menu
4. Click **+ New registration**
5. Enter the following information:
   - **Name**: Cognitive Hire Web Application
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: Web → `http://localhost:3000/auth/callback` (development environment)
6. Click **Register**

## 2. Configure the Web Application

### Add Production Redirect URI

1. Go to **Authentication**
2. Under **Platform configurations**, click **+ Add a platform** if needed or modify the existing Web platform
3. Add your production redirect URI (e.g., `https://app.cognitivehire.com/auth/callback`)
4. Under **Implicit grant and hybrid flows**, check:
   - **Access tokens**
   - **ID tokens**
5. Click **Save**

### Configure Logout URL

1. Still in the **Authentication** section
2. Under **Front-channel logout**, enter your logout URL:
   - Development: `http://localhost:3000/logout`
   - Production: `https://app.cognitivehire.com/logout`
3. Click **Save**

### Configure API Permissions

1. Go to **API permissions**
2. Click **+ Add a permission**
3. Select **My APIs**
4. Select your API application (e.g., **Cognitive Hire Recruitment API**)
5. Under **Delegated permissions**, select the `user_impersonation` scope
6. Click **Add permissions**
7. Additionally, add Microsoft Graph permissions:
   - Click **+ Add a permission**
   - Select **Microsoft Graph** → **Delegated permissions**
   - Select:
     - `openid`
     - `offline_access`
     - `profile`
     - `email`
   - Click **Add permissions**

### Generate a Client Secret

1. Go to **Certificates & secrets**
2. Click **+ New client secret**
3. Enter a description (e.g., "Web App Authentication")
4. Select an expiration period (e.g., 1 year, 2 years)
5. Click **Add**
6. **IMPORTANT**: Immediately copy and securely store the secret value, as you won't be able to see it again

## 3. Configure the User Flow

1. In your Azure AD B2C tenant, go to **User flows**
2. Click **+ New user flow**
3. Select **Sign up and sign in**
4. Select a version (B2C_1 recommended)
5. Enter a name (e.g., "signupsignin1")
6. Configure user attributes, application claims, and page layouts as needed
7. Click **Create**

## 4. Update Frontend Application Configuration

Update your frontend web application's `.env.local` file:

