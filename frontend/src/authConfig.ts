import { Configuration, PublicClientApplication } from "@azure/msal-browser";

// MSAL configuration
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID || "ecc67f5e-da53-418a-9e0f-b4cafff35d86",
    authority: process.env.NEXT_PUBLIC_AZURE_AUTHORITY || "https://cognitivehire.b2clogin.com/cognitivehire.onmicrosoft.com/B2C_1_cognitivehire",
    knownAuthorities: ["cognitivehire.b2clogin.com"],
    redirectUri: typeof window !== "undefined" ? `${window.location.origin}/auth/callback` : "http://localhost:3000/auth/callback",
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: true
  },
  system: {
    allowNativeBroker: false,
    loggerOptions: {
      logLevel: 3, // Verbose
      loggerCallback: (level, message) => {
        console.log(`MSAL [${level}]: ${message}`);
      },
      piiLoggingEnabled: false
    }
  }
};

// Authentication request scopes
export const loginRequest = {
  scopes: ["openid", "profile"],
  prompt: "select_account"
};

// Initialize in a way that's safe for HMR
let msalInstance: PublicClientApplication | null = null;

// Only create the instance once and protect against HMR
// This function ensures we don't try to recreate the instance during HMR
export function getMsalInstance() {
  if (typeof window === 'undefined') return null;
  
  if (!msalInstance) {
    try {
      msalInstance = new PublicClientApplication(msalConfig);
      
      // Handle any pending redirects
      msalInstance.handleRedirectPromise().catch(error => {
        console.error("MSAL Redirect Error:", error);
      });
    } catch (err) {
      console.error('Failed to initialize MSAL:', err);
    }
  }
  
  return msalInstance;
}

// Export the instance-getter function
export { msalInstance };
