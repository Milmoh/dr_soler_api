import os
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Security Scheme
security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Verifies the Bearer token against the API_BEARER_TOKEN environment variable.
    """
    token = credentials.credentials
    expected_token = os.getenv("API_BEARER_TOKEN")
    
    # If no token is set in env, we might want to fail safe or allow default for dev.
    # For security, let's assume it must be set.
    if not expected_token:
        # Fallback for local dev comfort if user forgot, but warn or ensure user sets it.
        # Ideally, we reject if not configured.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API_BEARER_TOKEN not configured on server"
        )

    if token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
