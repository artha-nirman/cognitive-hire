# Manual Testing Procedures for Azure AD B2C Integration

## Prerequisites
- Access to test Azure AD B2C tenant
- Test user credentials for different roles
- Frontend application running on localhost:3000
- Security service running on localhost:8000

## Test Cases

### 1. New User Registration
1. Access the frontend application
2. Click "Sign Up"
3. Verify redirect to Azure AD B2C sign-up page
4. Complete registration with new test credentials
5. Verify redirect back to application
6. Verify user profile is created with correct permissions

### 2. Existing User Login
1. Access the frontend application
2. Click "Login"
3. Enter test user credentials
4. Verify successful authentication
5. Verify correct permissions are applied

### 3. Password Reset Flow
1. Access the frontend application
2. Click "Login"
3. Click "Forgot Password"
4. Follow the password reset procedure
5. Verify new password works for authentication

### 4. Token Refresh
1. Login with test credentials
2. Wait until close to token expiration (check JWT expiration)
3. Perform an action requiring authentication
4. Verify token is refreshed automatically
5. Verify continued access to protected resources

### 5. Logout Flow
1. Login with test credentials
2. Click "Logout"
3. Verify session is ended
4. Verify protected routes are no longer accessible

## Documenting Results
Record all test results in the shared testing spreadsheet, including:
- Test date and time
- Test user used
- Success/failure status
- Screenshots of any errors
- Browser/environment details
