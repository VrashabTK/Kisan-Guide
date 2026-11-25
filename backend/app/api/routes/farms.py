"""
Farm Management & Daily Monitoring API Endpoints.
Provides farm registration, late-join progress tracking, dual timelines,
intelligent daily activity management, observations, and harvest logs.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Dict, Any, List, Optional
from datetime import date

from backend.app.core.security import get_current_user_id
from backend.app.schemas import (
    FarmCreate,
    FarmUpdate,
    FarmProgressCorrectionRequest,
    ActivityActionRequest,
    ObservationCreate,
    HarvestCreate,
)
from backend.app.agricultural_rules.crops import SUPPORTED_CROPS, DK_TALUKS
from backend.app.agricultural_rules.farm_lifecycle import (
    get_crop_stages,
    validate_stage_consistency
)
from backend.app.services.farm_service import (
    register_new_farm,
    get_user_farms_with_status,
    get_farm_detail,
    get_or_generate_daily_activities,
    mark_activity_done,
    mark_activity_skipped,
    correct_farm_progress,
    add_farm_observation,
    add_farm_harvest,
    calculate_farm_timeline
)
from backend.app.services.database import (
    get_farm_by_id_db,
    update_farm_db,
    delete_farm_db,
    get_farm_corrections_db,
    get_farm_activities_history_db,
    get_farm_activities_for_date_db,
    get_farm_observations_db,
    get_farm_harvests_db,
)

router = APIRouter(prefix="/farms", tags=["My Farm Management"])

# ==================== Crop Stages Info ====================

@router.get("/stages/{crop}")
async def get_stages_for_crop(crop: str):
    if crop not in SUPPORTED_CROPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported crop '{crop}'. Must be one of: {', '.join(SUPPORTED_CROPS)}"
        )
    return {
        "crop": crop,
        "stages": get_crop_stages(crop)
    }

# ==================== Farm CRUD ====================

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_farm(
    payload: FarmCreate,
    uid: str = Depends(get_current_user_id)
):
    # Validate crop
    if payload.crop not in SUPPORTED_CROPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Crop must be one of: {', '.join(SUPPORTED_CROPS)}"
        )
    # Validate taluk
    if payload.taluk not in DK_TALUKS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Taluk must be one of Dakshina Kannada's 9 taluks: {', '.join(DK_TALUKS.keys())}"
        )

    # Optional stage consistency warning check
    stage_warning = None
    if payload.current_stage and payload.initial_farming_day:
        stage_warning = validate_stage_consistency(
            payload.crop,
            payload.initial_farming_day,
            payload.current_stage
        )

    created_farm = await register_new_farm(payload.dict(), uid)
    if stage_warning:
        created_farm["stage_consistency_warning"] = stage_warning

    return created_farm

@router.get("")
async def list_farms(
    uid: str = Depends(get_current_user_id)
):
    return await get_user_farms_with_status(uid)

@router.get("/{farm_id}")
async def get_farm(
    farm_id: str,
    uid: str = Depends(get_current_user_id)
):
    farm = await get_farm_detail(farm_id, uid)
    if not farm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or unauthorized access"
        )
    return farm

@router.put("/{farm_id}")
async def update_farm(
    farm_id: str,
    payload: FarmUpdate,
    uid: str = Depends(get_current_user_id)
):
    existing = get_farm_by_id_db(farm_id, uid)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or unauthorized"
        )
    
    if payload.crop and payload.crop not in SUPPORTED_CROPS:
        raise HTTPException(status_code=400, detail="Invalid crop")
    if payload.taluk and payload.taluk not in DK_TALUKS:
        raise HTTPException(status_code=400, detail="Invalid taluk")

    updated = update_farm_db(farm_id, uid, payload.dict())
    timeline = calculate_farm_timeline(updated)
    return {
        **updated,
        "current_crop_day": timeline["crop_day"],
        "current_monitoring_day": timeline["monitoring_day"]
    }

@router.delete("/{farm_id}")
async def delete_farm(
    farm_id: str,
    uid: str = Depends(get_current_user_id)
):
    deleted = delete_farm_db(farm_id, uid)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or unauthorized"
        )
    return {"message": "Farm removed successfully", "farm_id": farm_id}

# ==================== Progress Correction ====================

@router.post("/{farm_id}/progress-correction")
async def update_farm_progress(
    farm_id: str,
    payload: FarmProgressCorrectionRequest,
    uid: str = Depends(get_current_user_id)
):
    res = await correct_farm_progress(
        farm_id=farm_id,
        user_id=uid,
        new_crop_day=payload.new_crop_day,
        new_stage=payload.new_stage,
        reason=payload.reason
    )
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farm not found or unauthorized"
        )
    return res

@router.get("/{farm_id}/corrections")
async def list_farm_corrections(
    farm_id: str,
    uid: str = Depends(get_current_user_id)
):
    farm = get_farm_by_id_db(farm_id, uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return get_farm_corrections_db(farm_id)

# ==================== Daily Activities ====================

@router.get("/{farm_id}/activities/today")
async def get_today_activities(
    farm_id: str,
    uid: str = Depends(get_current_user_id)
):
    farm = get_farm_by_id_db(farm_id, uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    activities = await get_or_generate_daily_activities(farm_id, uid)
    return activities

@router.post("/{farm_id}/activities/{activity_id}/complete")
async def complete_activity(
    farm_id: str,
    activity_id: str,
    uid: str = Depends(get_current_user_id)
):
    updated = await mark_activity_done(activity_id, farm_id, uid)
    if not updated:
        raise HTTPException(status_code=404, detail="Activity or farm not found")
    return updated

@router.post("/{farm_id}/activities/{activity_id}/skip")
async def skip_activity(
    farm_id: str,
    activity_id: str,
    payload: ActivityActionRequest,
    uid: str = Depends(get_current_user_id)
):
    updated = await mark_activity_skipped(activity_id, farm_id, uid, payload.reason)
    if not updated:
        raise HTTPException(status_code=404, detail="Activity or farm not found")
    return updated

@router.get("/{farm_id}/activities/history")
async def get_activities_history(
    farm_id: str,
    date_query: Optional[str] = Query(None, alias="date"),
    uid: str = Depends(get_current_user_id)
):
    farm = get_farm_by_id_db(farm_id, uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")

    mon_start_str = farm.get("monitoring_start_date") or date.today().isoformat()

    if date_query:
        # Check if date is prior to monitoring
        if date_query < mon_start_str:
            return {
                "farm_id": farm_id,
                "calendar_date": date_query,
                "is_prior_to_monitoring": True,
                "notice": "This date is prior to when KISSAN GUIDE monitoring began on this farm. Activity records were not tracked before this date.",
                "activities": [],
                "observations": []
            }
        
        target_d = date.fromisoformat(date_query)
        activities = await get_or_generate_daily_activities(farm_id, uid, target_d)
        timeline = calculate_farm_timeline(farm, target_d)
        
        # Get observations on that date
        all_obs = get_farm_observations_db(farm_id, limit=100)
        day_obs = [o for o in all_obs if o.get("calendar_date") == date_query]

        return {
            "farm_id": farm_id,
            "calendar_date": date_query,
            "crop_day": timeline["crop_day"],
            "monitoring_day": timeline["monitoring_day"],
            "is_prior_to_monitoring": False,
            "activities": activities,
            "observations": day_obs
        }

    # If no specific date, return full history list
    return get_farm_activities_history_db(farm_id, limit=100)

# ==================== Observations ====================

@router.post("/{farm_id}/observations", status_code=status.HTTP_201_CREATED)
async def save_observation(
    farm_id: str,
    payload: ObservationCreate,
    uid: str = Depends(get_current_user_id)
):
    if payload.farm_id != farm_id:
        payload.farm_id = farm_id
    res = await add_farm_observation(payload.dict(), uid)
    if not res:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")
    return res

@router.get("/{farm_id}/observations")
async def list_observations(
    farm_id: str,
    uid: str = Depends(get_current_user_id)
):
    farm = get_farm_by_id_db(farm_id, uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return get_farm_observations_db(farm_id, limit=50)

# ==================== Harvests ====================

@router.post("/{farm_id}/harvests", status_code=status.HTTP_201_CREATED)
async def record_harvest(
    farm_id: str,
    payload: HarvestCreate,
    uid: str = Depends(get_current_user_id)
):
    if payload.farm_id != farm_id:
        payload.farm_id = farm_id
    res = await add_farm_harvest(payload.dict(), uid)
    if not res:
        raise HTTPException(status_code=404, detail="Farm not found or unauthorized")
    return res

@router.get("/{farm_id}/harvests")
async def list_harvests(
    farm_id: str,
    uid: str = Depends(get_current_user_id)
):
    farm = get_farm_by_id_db(farm_id, uid)
    if not farm:
        raise HTTPException(status_code=404, detail="Farm not found")
    return get_farm_harvests_db(farm_id)
