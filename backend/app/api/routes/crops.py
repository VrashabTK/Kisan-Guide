from fastapi import APIRouter, Depends, Query
from typing import Optional, List, Dict, Any
from backend.app.core.security import get_current_user_id
from backend.app.schemas import CropRecommendationRequest
from backend.app.services.crop_service import recommend_crops
from backend.app.services.firebase_service import save_crop_recommendation, get_crop_recommendations

router = APIRouter(prefix="/crops", tags=["Crop Recommendation"])

@router.post("/recommend")
async def get_crop_recommendation(
    payload: CropRecommendationRequest,
    uid: Optional[str] = Depends(get_current_user_id)
):
    recommendation = await recommend_crops(
        taluk=payload.taluk,
        water_availability=payload.water_availability,
        soil_type=payload.soil_type,
        irrigation_available=payload.irrigation_available,
        previous_crop=payload.previous_crop,
        plantation_area_acres=payload.plantation_area_acres,
    )

    # Persist in user's recommendation history if authenticated
    if uid:
        try:
            await save_crop_recommendation(uid, recommendation)
        except Exception:
            pass

    return recommendation

@router.get("/recommendations")
async def list_user_recommendations(
    uid: str = Depends(get_current_user_id)
):
    return await get_crop_recommendations(uid)
