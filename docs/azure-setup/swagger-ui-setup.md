# Configuring Swagger UI with Azure AD B2C

This guide explains how to configure Swagger UI to work with Azure AD B2C authentication and troubleshoot common issues.

## 1. Register OAuth2 Redirect URI

Make sure the OAuth2 redirect URI is registered in your API application in Azure AD B2C:

1. Go to your API's application registration in Azure AD B2C
2. Navigate to **Authentication**
3. Under **Platform configurations**, click **+ Add a platform** and select **Web**
4. Add the OAuth2 redirect URI: `http://localhost:8000/docs/oauth2-redirect`
5. For production, add: `https://api.cognitivehire.com/docs/oauth2-redirect`
6. Click **Configure**

## 2. Configure FastAPI's OpenAPI Documentation

In your FastAPI application, ensure the Swagger UI is properly configured for Azure AD B2C:

```python
app = FastAPI(
    title="Recruitment Service API",
    description="API for managing job postings, employers, and candidate interactions",
    version="1.0.0",
    swagger_ui_oauth2_redirect_url="/docs/oauth2-redirect",
    swagger_ui_init_oauth={
        "usePkceWithAuthorizationCodeGrant": True,
        "clientId": settings.AZURE_AD_B2C_CLIENT_ID,
        "appName": "Cognitive Hire API Swagger UI",
        "scopeSeparator": " ",
        "scopes": ["openid", settings.azure_ad_b2c_scope]
    }
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add security scheme
    openapi_schema["components"] = openapi_schema.get("components", {})
    openapi_schema["components"]["securitySchemes"] = {
        "oauth2": {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/authorize",
                    "tokenUrl": f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/token",
                    "scopes": {
                        "openid": "OpenID Connect authentication",
                        settings.azure_ad_b2c_scope: "Access API"
                    }
                }
            }
        }
    }
    
    # Apply oauth2 security to all routes
    openapi_schema["security"] = [{"oauth2": settings.azure_ad_b2c_scopes}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

## 3. Verify CORS Configuration

Make sure your CORS settings allow requests from the Swagger UI:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 4. Test the Swagger UI Authentication

1. Navigate to your API's Swagger UI (e.g., `http://localhost:8000/docs`)
2. Click the **Authorize** button
3. Verify that the Azure AD B2C login screen appears
4. After successful authentication, you should be able to make authenticated API requests

## 5. Troubleshooting Common Issues

### Fixing "Insufficient Permissions" Error

If you encounter the error `AADB2C90205: This application does not have sufficient permissions against this web resource to perform the operation`, follow these steps:

#### 1. Enable App-to-App Authorization in Azure AD B2C

1. Sign in to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Azure AD B2C tenant
3. Select **App registrations**
4. Find and select your API application registration (not the web app)
5. Go to **Expose an API**
6. For the application ID URI (e.g., `https://cognitivehire.onmicrosoft.com/api`), check that the scope you defined is listed below
7. Ensure that the API scope (`user_impersonation` or similar) is set to **Enabled**
8. Note the full scope name (e.g., `https://cognitivehire.onmicrosoft.com/api/user_impersonation`)

#### 2. Grant Permission in the Client Application

1. Go back to **App registrations**
2. Find and select the *client application* (the app that Swagger UI uses)
3. Go to **API permissions**
4. Click **+ Add a permission**
5. Select **My APIs**
6. Select your API application
7. Under **Delegated permissions**, select the permission scope (`user_impersonation` or similar)
8. Click **Add permissions**
9. Click **Grant admin consent for [your tenant]** at the top of the API permissions page

#### 3. Update your API Configuration

Update your API's `.env` file with the correct scope information:
