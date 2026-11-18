import os
import logging
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
from backend.app.core.config import settings

logger = logging.getLogger("kissan_guide.security")

# Global Firebase Admin initialization state
_firebase_initialized = False

def init_firebase():
    global _firebase_initialized
    if _firebase_initialized:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials
        
        if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred, {
                'storageBucket': settings.FIREBASE_STORAGE_BUCKET or None
            })
            _firebase_initialized = True
            logger.info("Firebase Admin initialized successfully with credentials file.")
        else:
            logger.info("Firebase credentials not configured. Running in secure local developer mode.")
            _firebase_initialized = True
    except Exception as e:
        logger.warning(f"Firebase Admin initialization check: {e}. Dev mode active.")
        _firebase_initialized = True

async def get_current_user_claims(
    authorization: Optional[str] = Header(None, alias="Authorization")
) -> Dict[str, Any]:
    """
    Extracts and validates the Firebase ID token from the Authorization header.
    Returns decoded user claims including 'uid', 'email', 'phone_number', etc.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split("Bearer ")[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    init_firebase()

    # Try verifying through Firebase Admin SDK if available and configured
    if settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH):
        try:
            import firebase_admin
            from firebase_admin import auth
            if firebase_admin._apps:
                decoded_token = auth.verify_id_token(token)
                return decoded_token
        except Exception as e:
            logger.debug(f"Firebase token verification error: {e}")

    # Development & test tokens
    if settings.ENVIRONMENT.lower() in ["development", "test", "local"]:
        if token.startswith("dev-token:"):
            uid = token.replace("dev-token:", "")
            return {
                "uid": uid or "dev_farmer_123",
                "email": f"{uid}@kissanguide.local",
                "name": "Ramesh Gowda",
                "phone_number": "+919876543210",
                "is_dev": True
            }
        elif token == "mock-token" or token.startswith("demo-"):
            return {
                "uid": "farmer_dk_001",
                "email": "farmer@kissanguide.local",
                "name": "Kishan Kumar",
                "phone_number": "+919880011223",
                "is_dev": True
            }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token. Please re-authenticate.",
        headers={"WWW-Authenticate": "Bearer"},
    )

async def get_current_user_id(claims: Dict[str, Any] = Depends(get_current_user_claims)) -> str:
    uid = claims.get("uid")
    if not uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload missing UID",
        )
    return uid
