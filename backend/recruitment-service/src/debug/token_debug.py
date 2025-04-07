import base64
import json
import logging
import datetime
from fastapi import Request, HTTPException
import structlog
from typing import Dict, Any, Optional

from src.common.config import settings

logger = structlog.get_logger(__name__)

def decode_jwt_without_verification(token: str) -> Dict[str, Any]:
    """
    Decode JWT token without signature verification.
    
    This is only used for debugging. In production, tokens should always be
    fully verified before being trusted.
    
    Args:
        token: JWT token string
        
    Returns:
        Dictionary with token header and payload
    """
    parts = token.split('.')
    if len(parts) != 3:
        return {"error": "Invalid token format"}
    
    try:
        # Decode header
        header_part = parts[0]
        header_padded = header_part + '=' * (4 - len(header_part) % 4)
        header_bytes = base64.b64decode(header_padded.replace('-', '+').replace('_', '/'))
        header = json.loads(header_bytes.decode('utf-8'))
        
        # Decode payload
        payload_part = parts[1]
        payload_padded = payload_part + '=' * (4 - len(payload_part) % 4)
        payload_bytes = base64.b64decode(payload_padded.replace('-', '+').replace('_', '/'))
        payload = json.loads(payload_bytes.decode('utf-8'))
        
        return {
            "header": header,
            "payload": payload,
            "raw": {
                "header": header_part,
                "payload": payload_part,
                "signature": parts[2]
            }
        }
    except Exception as e:
        return {"error": f"Failed to decode token: {str(e)}"}

def get_auth_debug_info(request: Request) -> Dict[str, Any]:
    """
    Get detailed debug information about authentication.
    
    Args:
        request: The HTTP request
        
    Returns:
        Dictionary with auth debug information
    """
    auth_header = request.headers.get("Authorization", "")
    auth_bypass = request.headers.get("X-Auth-Bypass")
    token = None
    
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
    
    debug_info = {
        "auth_header_present": bool(auth_header),
        "auth_bypass_present": bool(auth_bypass),
        "auth_bypass_enabled": settings.AUTH_BYPASS_ENABLED,
        "token_present": bool(token),
        "environment": settings.ENVIRONMENT,
        "settings": {
            "environment": settings.ENVIRONMENT,
            "auth_bypass_enabled": settings.AUTH_BYPASS_ENABLED,
            "azure_ad_b2c_tenant": settings.AZURE_AD_B2C_TENANT_NAME,
            "azure_ad_b2c_policy": settings.AZURE_AD_B2C_SIGNIN_POLICY,
            "azure_ad_b2c_scope": settings.azure_ad_b2c_scope,
            "redirect_url": settings.oauth2_redirect_url
        }
    }
    
    if token:
        decoded_token = decode_jwt_without_verification(token)
        debug_info["token_info"] = decoded_token
        
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
    Get help information about authentication configuration.
    
    Returns:
        Dictionary with authentication help information
    """
    return {
        "authentication_methods": {
            "oauth2": {
                "swagger_authorize": {
                    "client_id": settings.AZURE_AD_B2C_CLIENT_ID,
                    "auth_url": f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/authorize",
                    "token_url": f"https://{settings.AZURE_AD_B2C_TENANT_NAME}.b2clogin.com/{settings.AZURE_AD_B2C_TENANT_NAME}.onmicrosoft.com/{settings.AZURE_AD_B2C_SIGNIN_POLICY}/oauth2/v2.0/token",
                    "scope": settings.azure_ad_b2c_scope
                }
            },
            "bearer_token": {
                "header": "Authorization: Bearer YOUR_TOKEN",
                "format": "JWT"
            },
            "auth_bypass": {
                "enabled": settings.AUTH_BYPASS_ENABLED,
                "environment": settings.ENVIRONMENT,
                "header": "X-Auth-Bypass",
                "token": settings.AUTH_BYPASS_TOKEN if settings.AUTH_BYPASS_ENABLED and settings.ENVIRONMENT in ["development", "testing"] else "hidden",
                "example": f'curl -H "X-Auth-Bypass: {settings.AUTH_BYPASS_TOKEN}" http://localhost:8000/api/employer/'
            }
        },
        "troubleshooting": {
            "debug_endpoints": {
                "token_info": "/debug/token-info",
                "auth_test": "/debug/auth-test"
            },
            "common_issues": [
                "Swagger UI: Make sure the client ID matches the Azure B2C app registration",
                "Auth Bypass: Verify X-Auth-Bypass header contains exact token from settings",
                "Bearer Token: Ensure token is not expired and has required scopes",
                "Azure B2C: Verify Azure settings match your B2C tenant configuration",
                "Scope: Ensure the app has permission to access the required scope"
            ]
        }
    }

def get_logging_debug_info() -> Dict[str, Any]:
    """
    Get information about logging configuration to help diagnose missing logs.
    
    Returns:
        Dictionary with logging configuration information
    """
    # Get Python logging configuration
    root_logger = logging.getLogger()
    auth_logger = logging.getLogger('src.common.auth')
    auth_deps_logger = logging.getLogger('src.common.auth.dependencies')
    employer_router_logger = logging.getLogger('src.domains.employer.router')
    
    # Check if loggers have handlers attached
    def get_logger_handlers(logger):
        handlers = []
        for handler in logger.handlers:
            handlers.append({
                "type": handler.__class__.__name__,
                "level": logging.getLevelName(handler.level),
                "formatter": handler.formatter.__class__.__name__ if hasattr(handler, "formatter") else None
            })
        return handlers
    
    # Get structlog configuration
    config = structlog.get_config()
    structlog_config = {
        "processors": [
            # Fix: Safely get processor name
            getattr(p, "__module__", str(p.__class__)) + "." + getattr(p, "__name__", p.__class__.__name__)
            for p in config.get("processors", [])
        ]
    }
    
    return {
        "python_logging": {
            "root_level": root_logger.level,
            "root_level_name": logging.getLevelName(root_logger.level),
            "handlers": get_logger_handlers(root_logger),
            "auth_level": auth_logger.level,
            "auth_level_name": logging.getLevelName(auth_logger.level),
            "auth_deps_level": auth_deps_logger.level,
            "auth_deps_level_name": logging.getLevelName(auth_deps_logger.level),
            "employer_router_level": employer_router_logger.level,
            "employer_router_level_name": logging.getLevelName(employer_router_logger.level),
            "auth_logger_propagate": auth_logger.propagate,
            "auth_deps_logger_propagate": auth_deps_logger.propagate,
            "employer_router_logger_propagate": employer_router_logger.propagate,
            "employer_router_handlers": get_logger_handlers(employer_router_logger),
        },
        "structlog_config": structlog_config,
        "app_config": {
            "environment": settings.ENVIRONMENT,
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT
        },
        "active_loggers": {
            name: logging.getLevelName(logging.getLogger(name).level)
            for name in logging.root.manager.loggerDict
            if "auth" in name.lower() or "employer" in name.lower() or "router" in name.lower()
        }
    }

def test_logging_methods():
    """Test different logging methods to find which ones work."""
    logger = structlog.get_logger(__name__)
    py_logger = logging.getLogger(__name__)
    
    # Test different logging methods
    print("[DEBUG-PRINT] Direct print test")
    
    py_logger.debug("Python logger DEBUG test")
    py_logger.info("Python logger INFO test")
    py_logger.warning("Python logger WARNING test")
    
    logger.debug("Structlog DEBUG test")
    logger.info("Structlog INFO test")
    logger.warning("Structlog WARNING test")
    
    return {
        "tests_executed": True,
        "methods_tested": ["print", "logging.debug/info/warning", "structlog.debug/info/warning"],
        "timestamp": datetime.datetime.utcnow().isoformat()
    }
