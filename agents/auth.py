"""Bearer-token authorization for non-public API operations."""
import os
import secrets

from typing import Optional

from fastapi import Header, HTTPException


def require_api_token(authorization: Optional[str] = Header(default=None)) -> None:
    """Fail closed when the deployment token is absent or invalid."""
    expected = os.environ.get("API_AUTH_TOKEN")
    if not expected:
        raise HTTPException(status_code=503, detail="API_AUTH_TOKEN is not configured")
    scheme, separator, supplied = (authorization or "").partition(" ")
    if scheme.lower() != "bearer" or not separator or not secrets.compare_digest(supplied, expected):
        raise HTTPException(
            status_code=401,
            detail="Valid bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
