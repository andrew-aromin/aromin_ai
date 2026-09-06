"""
Utility functions for Aromin AI backend.
Includes request sanitation and authentication token verification.
"""

import secrets
from typing import Optional

import bleach
import config
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Require Bearer token for protected endpoints
security = HTTPBearer(auto_error=True)


def sanitize_input(text: Optional[str]) -> str:
    """
    Sanitizes user input by stripping all HTML tags and attributes.
    Defense-in-depth measure to prevent XSS and unwanted HTML injection.

    Args:
        text: Raw input string or None.

    Returns:
        Sanitized plain text string.
    """
    if not text:
        return ""
    if not isinstance(text, str):
        text = str(text)
    # Strip all tags and attributes
    return bleach.clean(text, tags=[], attributes={}, strip=True).strip()


def verify_ingest_key(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    Verifies the Bearer token for ingestion requests using constant-time comparison.

    Args:
        credentials: The HTTP authorization credentials from the Authorization header.

    Raises:
        HTTPException 500: If the server does not have INGEST_API_KEY configured.
        HTTPException 403: If the provided token does not match the configured key.

    Returns:
        The validated token string.
    """
    expected_key = getattr(config, "INGEST_API_KEY", "")
    if not expected_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Security key not configured.",
        )

    # Constant-time comparison to protect against timing attacks
    if not secrets.compare_digest(credentials.credentials, expected_key):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key.",
        )

    return credentials.credentials
