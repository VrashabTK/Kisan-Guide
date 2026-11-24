from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, Optional
import logging

from backend.app.core.security import get_current_user_claims, get_current_user_id
from backend.app.schemas import (
    UserProfileUpdate,
    SignUpRequest,
    LoginRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    CropPreferenceUpdate,
)
from backend.app.services.database import (
    create_user,
    authenticate_user,
    create_password_reset_token,
    reset_password,
    get_user_by_id,
    update_user_profile as update_user_profile_db,
    update_crop_preference,
    VALID_CROPS,
)
from backend.app.services.firebase_service import (
    get_user_profile as get_fb_profile,
    update_user_profile as update_fb_profile,
    delete_user_account as delete_fb_account
)

logger = logging.getLogger("kissan_guide.routes.auth")

router = APIRouter(tags=["Authentication & Users"])

# ==================== Authentication Routes ====================

@router.post("/auth/signup", status_code=status.HTTP_201_CREATED)
async def signup(payload: SignUpRequest):
    """
    Registers a new user using either Email OR Indian Mobile Number + Password.
    Strictly checks for existence prior to creation.
    Hashes password with Argon2id and returns persistent profile + JWT token.
    """
    if payload.confirm_password and payload.password != payload.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password and confirm password do not match."
        )

    try:
        result = create_user(
            identifier=payload.identifier,
            password=payload.password,
            full_name=payload.full_name,
            taluk=payload.taluk or "Mangaluru"
        )
        return result
    except ValueError as e:
        err_msg = str(e)
        if "already exists" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address or mobile number already exists. Please log in."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=err_msg
        )
    except Exception as e:
        logger.error(f"Signup error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register account. Please try again."
        )

@router.post("/auth/login")
async def login(payload: LoginRequest):
    """
    Authenticates a user using registered Email OR Mobile Number + Password.
    Verifies Argon2id password hash with brute-force rate-limiting.
    Does not disclose whether an account exists on failure.
    """
    try:
        result = authenticate_user(
            identifier=payload.identifier,
            password=payload.password
        )
        return result
    except ValueError as e:
        err_msg = str(e)
        if "too many failed" in err_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=err_msg
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check your email/mobile number and password."
        )
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during authentication. Please try again."
        )

@router.post("/auth/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    """
    Dispatches a password reset token for registered email or mobile number.
    Only succeeds if account actually exists in database.
    """
    try:
        result = create_password_reset_token(payload.identifier)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Forgot password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process password reset at this time."
        )

@router.post("/auth/reset-password")
async def perform_reset_password(payload: ResetPasswordRequest):
    """
    Resets password using a validated, non-expired token.
    """
    if payload.confirm_new_password and payload.new_password != payload.confirm_new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation do not match."
        )

    try:
        success = reset_password(payload.token, payload.new_password)
        if success:
            return {
                "success": True,
                "message": "Password reset successfully. You can now log in with your new password."
            }
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password reset failed.")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Reset password error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password."
        )

@router.post("/auth/logout")
async def logout():
    """Confirms user logout."""
    return {"success": True, "message": "Successfully logged out."}

# ==================== User Profile & Crop Preference ====================

@router.get("/users/me")
async def get_my_profile(
    claims: Dict[str, Any] = Depends(get_current_user_claims)
):
    """
    Returns the authenticated farmer's profile, including the currently selected crop.
    """
    uid = claims["uid"]
    # Check persistent SQLite first
    profile = get_user_by_id(uid)
    if profile:
        return profile

    # Fallback to Firebase or in-memory
    fb_profile = await get_fb_profile(uid)
    if fb_profile:
        return fb_profile

    return {
        "uid": uid,
        "fullName": claims.get("name", "Farmer"),
        "email": claims.get("email", ""),
        "phoneNumber": claims.get("phone_number", ""),
        "taluk": "Mangaluru",
        "district": "Dakshina Kannada",
        "state": "Karnataka",
        "preferredLanguage": "en",
        "selected_crop": "Arecanut",
        "selectedCrop": "Arecanut",
        "primaryCrops": ["Coconut", "Arecanut"],
    }

@router.put("/users/me")
async def update_my_profile(
    updates: UserProfileUpdate,
    uid: str = Depends(get_current_user_id)
):
    """
    Updates user profile details (taluk, preferred language, crop selections, etc.).
    """
    update_dict = updates.model_dump(exclude_unset=True)
    # Check if user exists in SQLite
    existing_sqlite = get_user_by_id(uid)
    if existing_sqlite:
        updated = update_user_profile_db(uid, update_dict)
        return updated

    # Fallback
    updated = await update_fb_profile(uid, update_dict)
    return updated

@router.get("/users/me/crop-preference")
async def get_my_crop_preference(
    claims: Dict[str, Any] = Depends(get_current_user_claims)
):
    """
    Gets the farmer's currently selected crop preference.
    """
    uid = claims["uid"]
    profile = get_user_by_id(uid) or await get_fb_profile(uid)
    crop = (profile.get("selected_crop") or profile.get("selectedCrop") or "Arecanut") if profile else "Arecanut"
    return {"crop": crop}

@router.put("/users/me/crop-preference")
async def set_my_crop_preference(
    payload: CropPreferenceUpdate,
    uid: str = Depends(get_current_user_id)
):
    """
    Saves the selected crop as the farmer's global preference across Crop, Weather, and Storage modules.
    Validates crop is one of Coconut, Rice, Arecanut, Cocoa.
    """
    if payload.crop not in VALID_CROPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid crop '{payload.crop}'. Supported crops: {list(VALID_CROPS)}"
        )

    existing_sqlite = get_user_by_id(uid)
    if existing_sqlite:
        updated = update_crop_preference(uid, payload.crop)
        return {"success": True, "selected_crop": payload.crop, "user": updated}

    # Fallback update
    await update_fb_profile(uid, {"selected_crop": payload.crop, "selectedCrop": payload.crop})
    return {"success": True, "selected_crop": payload.crop}

@router.delete("/users/me")
async def delete_my_account(
    uid: str = Depends(get_current_user_id)
):
    """Permanently deletes the farmer's account."""
    success = await delete_fb_account(uid)
    return {"success": success, "message": "Account successfully removed."}
