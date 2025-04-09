import { PublicClientApplication, Configuration, LogLevel, AccountInfo } from '@azure/msal-browser';

// Configuration constants - hardcoded for reliability
const CLIENT_ID = 'ecc67f5e-da53-418a-9e0f-b4cafff35d86';
const AUTHORITY = 'https://cognitivehire.b2clogin.com/cognitivehire.onmicrosoft.com/B2C_1_cognitivehire';
const REDIRECT_URI = 'http://localhost:3000/auth/callback';

// Create a simple class to manage authentication
class AuthService {
  private msalInstance: PublicClientApplication | null = null;
  private initialized = false;

  // Initialize MSAL
  async initialize(): Promise<boolean> {
    // Skip if already initialized
    if (this.initialized && this.msalInstance) {
      return true;
    }

    // Skip if not in browser
    if (typeof window === 'undefined') {
      return false;
    }

    try {
      // Configure MSAL with hardcoded values for reliability
      const config: Configuration = {
        auth: {
          clientId: CLIENT_ID,
          authority: AUTHORITY,
          redirectUri: REDIRECT_URI,
          knownAuthorities: ['cognitivehire.b2clogin.com'],
          navigateToLoginRequestUrl: true
        },
        cache: {
          cacheLocation: 'localStorage',
          storeAuthStateInCookie: true
        },
        system: {
          loggerOptions: {
            logLevel: LogLevel.Verbose,
            loggerCallback: (level, message) => {
              console.log(`MSAL [${level}]: ${message}`);
            }
          }
        }
      };

      // Create and initialize MSAL instance
      this.msalInstance = new PublicClientApplication(config);
      await this.msalInstance.initialize();
      this.initialized = true;
      return true;
    } catch (error) {
      console.error('Failed to initialize auth service:', error);
      return false;
    }
  }

  // Get current user account
  getCurrentUser(): AccountInfo | null {
    if (!this.msalInstance) return null;
    const accounts = this.msalInstance.getAllAccounts();
    return accounts[0] || null;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return this.getCurrentUser() !== null;
  }

  // Trigger login redirect
  async login(): Promise<void> {
    await this.initialize();
    if (!this.msalInstance) throw new Error('Auth service not initialized');
    
    return this.msalInstance.loginRedirect({
      scopes: ['openid', 'profile', 'email']
    });
  }

  // Handle redirect promise
  async handleRedirectPromise() {
    await this.initialize();
    if (!this.msalInstance) return null;
    
    return this.msalInstance.handleRedirectPromise();
  }

  // Log out
  async logout(): Promise<void> {
    await this.initialize();
    if (!this.msalInstance) return;
    
    const account = this.getCurrentUser();
    if (account) {
      return this.msalInstance.logoutRedirect({
        account
      });
    }
  }
}

// Export as singleton
export const authService = new AuthService();
