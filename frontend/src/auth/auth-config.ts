import { Configuration } from "@azure/msal-browser";

// MSAL configuration based on environment variables
export const msalConfig: Configuration = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID || "",
    authority: process.env.NEXT_PUBLIC_AZURE_AUTHORITY || "",
    redirectUri: typeof window !== "undefined" ? 
      `${window.location.origin}/auth/callback` : 
      "http://localhost:3000/auth/callback",
    knownAuthorities: ["cognitivehire.b2clogin.com"],
  },
  cache: {
    cacheLocation: "localStorage",
    storeAuthStateInCookie: true
  }
};

// Standard authentication request scopes for Azure AD B2C
export const loginRequest = {
  scopes: ["openid", "profile", "email"]
};
