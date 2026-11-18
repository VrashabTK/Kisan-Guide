from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from backend.app.core.security import get_current_user_id
from backend.app.schemas import NotificationPreferencesUpdate
from backend.app.services.firebase_service import (
    get_notifications,
    mark_notification_read,
    get_notification_preferences,
    update_notification_preferences
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
async def list_user_notifications(
    uid: str = Depends(get_current_user_id)
):
    return await get_notifications(uid)

@router.put("/{notification_id}/read")
async def mark_read(
    notification_id: str,
    uid: str = Depends(get_current_user_id)
):
    success = await mark_notification_read(uid, notification_id)
    return {"success": success}

@router.get("/preferences")
async def get_preferences(
    uid: str = Depends(get_current_user_id)
):
    return await get_notification_preferences(uid)

@router.put("/preferences")
async def update_preferences(
    prefs: NotificationPreferencesUpdate,
    uid: str = Depends(get_current_user_id)
):
    updated = await update_notification_preferences(uid, prefs.model_dump(exclude_unset=True))
    return updated
