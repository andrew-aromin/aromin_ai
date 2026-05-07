from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import bleach
from config import INGEST_API_KEY

security = HTTPBearer()

def sanitize_input(text: str) -> str:
    """
    Sanitizes user input by stripping all HTML tags and attributes.
    This is a defense-in-depth measure to prevent XSS and other injection attacks.
    """
    if not text:
        return ""
    # Strip all tags and attributes
    return bleach.clean(text, tags=[], attributes={}, strip=True).strip()

def verify_ingest_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifies the Bearer token for ingestion requests."""
    if not INGEST_API_KEY:
        # If no key is set, the endpoint is effectively disabled or open depending on policy.
        # Here we require it to be set and match.
        raise HTTPException(status_code=500, detail="Security key not configured.")
    
    if credentials.credentials != INGEST_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API Key.")
    return credentials.credentials
