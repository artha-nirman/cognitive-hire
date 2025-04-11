import { PublicClientApplication, AccountInfo } from '@azure/msal-browser';
import { msalConfig, loginRequest } from './auth-config';

// Create singleton MSAL instance
const msalInstance = typeof window !== 'undefined' ? 
  new PublicClientApplication(msalConfig) : null;

/**
 * Authentication service for Azure AD B2C integration
 * Follows Microsoft identity platform best practices
 */
class AuthService {
  /**
   * Get the current authenticated user
   * @returns {AccountInfo | null} The current user account or null if not authenticated
   */
  getCurrentUser(): AccountInfo | null {
    if (!msalInstance) return null;
    const accounts = msalInstance.getAllAccounts();
    return accounts.length > 0 ? accounts[0] : null;
  }

  /**
   * Check if the user is authenticated
   * @returns {boolean} True if authenticated, false otherwise
   */
  isAuthenticated(): boolean {
    return this.getCurrentUser() !== null;
  }

  /**
   * Initiate login with redirect
   * @returns {Promise<void>}
   */
  login(): Promise<void> {
    if (!msalInstance) throw new Error('MSAL not initialized');
    return msalInstance.loginRedirect(loginRequest);
  }

  /**
   * Process authentication redirect
   * @returns {Promise<void>}
   */
  handleRedirect(): Promise<any> {
    if (!msalInstance) return Promise.resolve(null);
    return msalInstance.handleRedirectPromise();
  }

  /**
   * Sign out the current user
   * @returns {Promise<void>}
   */
  logout(): Promise<void> {
    if (!msalInstance) {
      window.location.href = '/login';
      return Promise.resolve();
    }

    return msalInstance.logoutRedirect({
      postLogoutRedirectUri: `${window.location.origin}/login`
    });
  }
}

// Export singleton instance
export const authService = new AuthService();

// Export MSAL instance for context provider
export { msalInstance };
