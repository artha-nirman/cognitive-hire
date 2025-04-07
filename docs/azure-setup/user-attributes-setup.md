# Configuring Azure AD B2C User Attributes and Claims

This guide explains how to configure user attributes and claims in Azure AD B2C for the Cognitive Hire application.

## 1. Add Custom User Attributes

1. In your Azure AD B2C tenant, navigate to **User attributes**
2. Click **+ Add**
3. Enter the following information:
   - **Name**: OrganizationId
   - **Data Type**: String
4. Click **Create**
5. Repeat to add other custom attributes:
   - `JobTitle` (String)
   - `Department` (String)
   - `UserRole` (String)

## 2. Configure User Flow to Collect and Return Attributes

1. Navigate to **User flows**
2. Select your sign-up/sign-in user flow
3. Click **User attributes**
4. Under **Collect attribute**:
   - Check the attributes you want to collect during sign-up
   - At minimum, select: Email Address, Given Name, Surname
   - Optionally add JobTitle and Department
5. Under **Return claim**:
   - Select all attributes that should be included in the tokens
   - Include: Email Address, Given Name, Surname, User's Object ID
   - Also include: JobTitle, Department, OrganizationId, UserRole
6. Click **Save**

## 3. Customize Page Layout (Optional)

1. In your user flow, click **Page layouts**
2. Select **Local account sign up page**
3. Toggle **Use custom page content** to Yes
4. Customize the HTML as needed
5. Repeat for other pages
6. Click **Save**

## 4. Configure Application Claims in the JWT

1. Go to your API application registration
2. Select **Token configuration**
3. Click **+ Add optional claim**
4. Select **ID token**
5. Check the claims you want to include:
   - `email`
   - `family_name`
   - `given_name`
   - `name`
   - Any custom claims you created
6. Click **Add**
7. Repeat for **Access token**

## 5. Map Custom Attributes to Token Claims

To ensure custom attributes are included in tokens:

1. Go to your user flow
2. Click **Application claims**
3. Select all the standard and custom claims you want in the token
4. Click **Save**

## 6. Configure Application Roles and Claims

If you're using app roles:

1. Go to your API application registration
2. Navigate to **App roles**
3. For each role you created, make sure they're assigned to appropriate users/groups
4. In the **Manifest**, verify that `"groupMembershipClaims": "ApplicationGroup"`

## 7. Verify Token Claims in Your Application

After configuring attributes and claims, you can verify them in your application:

1. Create a debug endpoint in your API:

```python
@app.get("/debug/token-info", include_in_schema=False)
async def token_info(request: Request):
    """Debug endpoint to view token claims."""
    if settings.ENVIRONMENT != "development":
        raise HTTPException(status_code=404, detail="Not found")
    
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        try:
            # Decode without verification for debugging
            payload = jwt.decode(token, options={"verify_signature": False})
            return {
                "token_claims": payload,
                "user_info": {
                    "name": payload.get("name"),
                    "email": payload.get("emails", [payload.get("email")])[0],
                    "roles": payload.get("roles", []),
                    "organization_id": payload.get("extension_OrganizationId"),
                    "user_role": payload.get("extension_UserRole")
                }
            }
        except Exception as e:
            return {"error": str(e)}
    
    return {"error": "No authorization token found"}
```

2. Log in to your application
3. Access the debug endpoint to see the claims in your token

With these configurations, your application will have access to the necessary user attributes and claims for personalization and authorization.
