from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from backend.app.core.security import get_current_user_claims, get_current_user_id
from backend.app.services.firebase_service import (
    get_user_profile,
    update_user_profile,
    delete_user_account
)
from backend.app.schemas import UserProfileUpdate

router = APIRouter(prefix="/users", tags=["Users & Authentication"])

@router.get("/me")
async def get_my_profile(
    claims: Dict[str, Any] = Depends(get_current_user_claims)
):
    uid = claims["uid"]
    profile = await get_user_profile(uid)
    if not profile:
        profile = {
            "uid": uid,
            "fullName": claims.get("name", "Farmer"),
            "email": claims.get("email", ""),
            "phoneNumber": claims.get("phone_number", ""),
            "taluk": "Mangaluru",
            "district": "Dakshina Kannada",
            "state": "Karnataka",
            "preferredLanguage": "en",
            "primaryCrops": ["Coconut", "Arecanut"],
        }
    return profile

@router.put("/me")
async def update_my_profile(
    updates: UserProfileUpdate,
    uid: str = Depends(get_current_user_id)
):
    update_dict = updates.model_dump(exclude_unset=True)
    updated = await update_user_profile(uid, update_dict)
    return updated

@router.delete("/me")
async def delete_my_account(
    uid: str = Depends(get_current_user_id)
):
    success = await delete_user_account(uid)
    return {"success": success, "message": "Account successfully removed."}
