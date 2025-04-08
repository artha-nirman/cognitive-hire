import { test, expect } from '@playwright/test';

test.describe('Authentication Flow with Azure AD B2C', () => {
  test.use({
    // Use test credentials from environment variables
    storageState: { cookies: [], origins: [] }
  });
  
  test('Complete sign-in journey', async ({ page }) => {
    // Start the login process
    await page.goto('/login');
    await page.click('button:has-text("Sign in with Azure AD B2C")');
    
    // Wait for redirect to Azure AD B2C
    await page.waitForURL(/.*b2clogin.com.*/);
    
    // Fill in credentials on the Azure AD B2C page
    await page.fill('input[name="email"]', process.env.TEST_USER_EMAIL);
    await page.fill('input[name="password"]', process.env.TEST_USER_PASSWORD);
    await page.click('button:has-text("Sign in")');
    
    // Wait for redirect back to application
    await page.waitForURL(/.*\/dashboard.*/);
    
    // Verify authenticated state
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
    
    // Verify correct user is logged in
    const userName = await page.locator('[data-testid="user-name"]').textContent();
    expect(userName).toContain('Test User');
  });
  
  // Additional E2E test cases
});
