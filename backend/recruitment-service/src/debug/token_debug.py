import base64
import json
from fastapi import Request
import structlog
from typing import Dict, Any, Optional
from jose import jwt

from src.common.config import settings

logger = structlog.get_logger(__name__)

def get_auth_debug_info(request: Request) -> Dict[str, Any]:
    """
    Get detailed authentication debug information from a request.
    
    Args:
        request: The HTTP request
        
    Returns:
        Dict with authentication debug information
    """
    auth_header = request.headers.get("Authorization")
    debug_info = {
        "has_auth_header": auth_header is not None,
        "header_starts_with_bearer": auth_header and auth_header.startswith("Bearer ") or False,
        "auth_settings": {
            "tenant": settings.AZURE_AD_B2C_TENANT_NAME,
            "client_id": settings.AZURE_AD_B2C_CLIENT_ID,
            "policy": settings.AZURE_AD_B2C_SIGNIN_POLICY,
            "bypass_enabled": settings.AUTH_BYPASS_ENABLED,
        },
        "token_info": None,
        "decoded_payload": None,
        "decoded_header": None,
        "bypass_info": {
            "has_bypass_header": request.headers.get("X-Auth-Bypass") is not None,
            "bypass_token_valid": request.headers.get("X-Auth-Bypass") == settings.AUTH_BYPASS_TOKEN,
            "has_tenant_header": request.headers.get("X-Test-Tenant-ID") is not None,
        }
    }
    
    # Add authentication URLs
    debug_info["auth_urls"] = {
        "authority": settings.authority_url,
        "openid_config": settings.openid_config_url,
        "expected_scope": settings.azure_ad_b2c_scope
    }
    
    # Only try to decode the token in the Authorization header if it exists
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        
        # Add token segments info
        segments = token.split(".")
        debug_info["token_info"] = {
            "segment_count": len(segments),
            "is_jwt_format": len(segments) == 3,
            "length": len(token)
        }
        
        # Try to decode the token parts without validation
        try:
            # JWT has three parts: header.payload.signature
            if len(segments) >= 2:
                # Decode header (first segment)
                header_json = base64_decode_segment(segments[0])
                debug_info["decoded_header"] = json.loads(header_json) if header_json else None
                
                # Decode payload (second segment)
                payload_json = base64_decode_segment(segments[1])
                debug_info["decoded_payload"] = json.loads(payload_json) if payload_json else None
                
                # Extract key claims for easier viewing
                if debug_info["decoded_payload"]:
                    debug_info["key_claims"] = extract_key_claims(debug_info["decoded_payload"])
        except Exception as e:
            debug_info["decode_error"] = str(e)
    
    return debug_info

def extract_key_claims(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract the most important claims from a JWT payload."""
    key_claims = {}
    
    # Standard claims
    for claim in ["sub", "iat", "exp", "aud", "iss", "name", "email", "roles"]:
        if claim in payload:
            key_claims[claim] = payload[claim]
    
    # Handle expiration specially to show if token is expired
    if "exp" in payload:
        import time
        now = int(time.time())
        expires_in = payload["exp"] - now
        key_claims["expires_in_seconds"] = expires_in
        key_claims["is_expired"] = expires_in <= 0
    
    # Azure AD B2C specific claims
    for claim in ["idp", "tid", "oid", "emails", "tfp"]:
        if claim in payload:
            key_claims[claim] = payload[claim]
    
    # Add scope information if available
    for scope_claim in ["scp", "scope"]:
        if scope_claim in payload:
            if isinstance(payload[scope_claim], str):
                scopes = payload[scope_claim].split()
                key_claims["scopes"] = scopes
            else:
                key_claims["scopes"] = payload[scope_claim]
            
            # Check if our required scope is present
            required_scope = settings.azure_ad_b2c_scope
            key_claims["has_required_scope"] = (
                required_scope in key_claims.get("scopes", [])
            )
    
    return key_claims

def base64_decode_segment(segment: str) -> Optional[str]:
    """
    Decode a base64url-encoded JWT segment.
    
    Args:
        segment: The base64url-encoded segment
        
    Returns:
        Decoded string or None if decoding fails
    """
    try:
        # JWT uses base64url encoding (different from standard base64)
        # We need to add padding and replace URL-safe chars
        segment = segment.replace("-", "+").replace("_", "/")
        
        # Add padding if needed
        padding = len(segment) % 4
        if padding:
            segment += "=" * (4 - padding)
            
        return base64.b64decode(segment).decode('utf-8')
    except Exception as e:
        logger.warning(f"Failed to decode base64 segment: {str(e)}")
        return None

def get_auth_help_info() -> Dict[str, Any]:
    """
    Get authentication help information for developers.
    
    Returns:
        Dict with authentication help information
    """
    # Authorization code flow URL construction
    redirect_uri = "http://localhost:8000/docs/oauth2-redirect.html"
    
    auth_url = (
        f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/"
        f"{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/"
        f"{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/authorize"
        f"?client_id={settings.AZURE_AD_B2C_CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={redirect_uri}"
        f"&response_mode={settings.AZURE_AD_B2C_RESPONSE_MODE}"
        f"&scope=openid%20{settings.azure_ad_b2c_scope}"
    )
    
    token_url = (
        f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/"
        f"{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/"
        f"{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/token"
    )
    
    help_info = {
        "authorization_methods": [
            {
                "name": "Azure AD B2C OAuth 2.0",
                "description": "Use the Azure AD B2C configured for this application",
                "urls": {
                    "authorization_endpoint": auth_url,
                    "token_endpoint": token_url,
                    "redirect_uri": redirect_uri,
                    "openid_configuration": settings.openid_config_url,
                },
                "required_parameters": {
                    "client_id": settings.AZURE_AD_B2C_CLIENT_ID,
                    "response_type": "code",
                    "redirect_uri": redirect_uri,
                    "scope": f"openid {settings.azure_ad_b2c_scope}",
                    "response_mode": settings.AZURE_AD_B2C_RESPONSE_MODE,
                }
            },
            {
                "name": "Development Auth Bypass",
                "description": "Use the development authentication bypass mechanism (for development only)",
                "available": settings.AUTH_BYPASS_ENABLED and settings.ENVIRONMENT in ["development", "testing"],
                "usage": {
                    "header": "X-Auth-Bypass",
                    "value": settings.AUTH_BYPASS_TOKEN,
                    "optional_tenant_header": "X-Test-Tenant-ID",
                    "optional_tenant_value": "Any valid tenant ID for testing"
                }
            }
        ],
        "swagger_ui_config": {
            "client_id": settings.SWAGGER_UI_CLIENT_ID,
            "client_name": "Swagger UI",
            "redirect_url": settings.SWAGGER_UI_OAUTH_REDIRECT_URL,
            "pkce_enabled": True,
            "scopes": ["openid", settings.azure_ad_b2c_scope],
        },
        "troubleshooting": {
            "common_issues": [
                {
                    "problem": "Token validation fails with 'Invalid audience'",
                    "solution": "Ensure your token's 'aud' claim matches the client_id"
                },
                {
                    "problem": "Missing required scope",
                    "solution": f"Ensure your token contains the scope '{settings.azure_ad_b2c_scope}'"
                },
                {
                    "problem": "PKCE validation fails",
                    "solution": "Use a PKCE-capable client and ensure code_verifier is properly passed when exchanging the code"
                }
            ],
            "debug_endpoints": [
                {
                    "url": "/debug/token-info",
                    "description": "Get detailed information about your authentication token"
                },
                {
                    "url": "/debug/auth-test",
                    "description": "Test if your authentication is working correctly"
                }
            ]
        }
    }
    
    return help_info
