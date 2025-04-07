# Setting Up Azure AD B2C for the Recruitment API

This guide provides step-by-step instructions for registering and configuring the Recruitment API in Azure AD B2C.

## 1. Register the API Application

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure AD B2C tenant
3. Select **App registrations** from the left menu
4. Click **+ New registration**
5. Enter the following information:
   - **Name**: Cognitive Hire Recruitment API
   - **Supported account types**: Accounts in this organizational directory only
   - **Redirect URI**: (Leave blank for now)
6. Click **Register**

## 2. Configure the API Application

### Set Application ID URI

1. In your newly registered app, go to **Expose an API**
2. Click **+ Add** next to **Application ID URI**
3. Accept the default value or customize it (e.g., `https://cognitivehire.onmicrosoft.com/recruitment-api`)
4. Click **Save**

### Define API Scopes

1. Still in the **Expose an API** section, click **+ Add a scope**
2. Fill in the following values:
   - **Scope name**: `user_impersonation`
   - **Admin consent display name**: Access Recruitment API
   - **Admin consent description**: Allows the application to access the Recruitment API on behalf of the user
   - **State**: Enabled
3. Click **Add scope**

### Configure App Roles (Optional)

1. Go to **App roles**
2. Click **+ Create app role**
3. Fill in the following values:
   - **Display name**: Administrator
   - **Value**: Admin
   - **Description**: Full access to organization data
   - **Do you want to enable this app role?**: Yes
   - **Allowed member types**: Both (Users/Groups + Applications)
4. Click **Apply**
5. Repeat to create additional roles (e.g., "Recruiter", "HiringManager")

### Configure Application Manifest

1. Go to **Manifest**
2. Locate the `accessTokenAcceptedVersion` property and change its value from `null` to `2`
3. Click **Save**

## 3. Configure API Permissions

1. Go to **API permissions**
2. Click **+ Add a permission**
3. Select **Microsoft Graph** → **Delegated permissions**
4. Select the following permissions:
   - `openid`
   - `offline_access`
   - `profile`
5. Click **Add permissions**

## 4. Generate a Client Secret (for Server-to-Server Auth)

1. Go to **Certificates & secrets**
2. Click **+ New client secret**
3. Enter a description (e.g., "API Server Authentication")
4. Select an expiration period (e.g., 1 year, 2 years)
5. Click **Add**
6. **IMPORTANT**: Immediately copy and securely store the secret value, as you won't be able to see it again

## 5. CORS Settings for Swagger UI

1. In your FastAPI application configuration, add the Azure B2C login domain to your CORS allowlist:
   ```python
   CORS_ORIGINS = ["http://localhost:3000", "https://app.cognitivehire.com", "https://cognitivehire.b2clogin.com"]
   ```

## 6. Update Environment Configuration

Update your API `.env` file with the following values:

