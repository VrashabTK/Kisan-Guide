from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional, List, Dict, Any
from backend.app.core.security import get_current_user_id
from backend.app.schemas import StorageRecommendationRequest
from backend.app.services.storage_service import recommend_storage_practices
from backend.app.services.firebase_service import save_storage_record, get_storage_records

router = APIRouter(prefix="/storage", tags=["Storage Assistant"])

@router.post("/recommend")
async def get_storage_recommendation(
    payload: StorageRecommendationRequest,
    uid: Optional[str] = Depends(get_current_user_id)
):
    recommendation = await recommend_storage_practices(
        crop=payload.crop,
        harvest_date=payload.harvest_date,
        storage_method=payload.storage_method,
        crop_condition=payload.crop_condition,
        taluk=payload.taluk or "Mangaluru",
        quantity_kg=payload.quantity_kg,
        storage_facility_description=payload.storage_facility_description,
    )

    if uid:
        try:
            await save_storage_record(uid, recommendation)
        except Exception:
            pass

    return recommendation

@router.get("/history")
async def list_user_storage_records(
    uid: str = Depends(get_current_user_id)
):
    return await get_storage_records(uid)

@router.get("/{storage_id}")
async def get_storage_record(
    storage_id: str,
    uid: str = Depends(get_current_user_id)
):
    records = await get_storage_records(uid)
    for r in records:
        if r.get("storageId") == storage_id:
            return r
    raise HTTPException(status_code=404, detail="Storage record not found")
