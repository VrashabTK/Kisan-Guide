from fastapi import APIRouter, Depends
from typing import Dict, Any
from backend.app.schemas import AIStorageAssistantRequest
from backend.app.services.ai_service import generate_ai_storage_suggestions
from backend.app.services.storage_service import recommend_storage_practices
from backend.app.services.weather_service import get_weather

router = APIRouter(prefix="/ai", tags=["AI Agricultural Assistant"])

@router.post("/storage-assistant")
async def get_ai_storage_advice(
    payload: AIStorageAssistantRequest
):
    taluk = payload.taluk or "Mangaluru"
    weather_data = await get_weather(taluk)
    current_weather = weather_data.get("current", {})

    rule_evaluation = await recommend_storage_practices(
        crop=payload.crop,
        harvest_date=payload.harvest_date,
        storage_method=payload.storage_method,
        crop_condition=payload.crop_condition,
        taluk=taluk,
    )

    ai_result = await generate_ai_storage_suggestions(
        crop=payload.crop,
        harvest_date=payload.harvest_date,
        storage_method=payload.storage_method,
        crop_condition=payload.crop_condition,
        taluk=taluk,
        weather_summary=current_weather,
        rule_evaluation=rule_evaluation,
        language=payload.language or "en"
    )

    return {
        "crop": payload.crop,
        "taluk": taluk,
        "ai_suggestions": ai_result,
        "rule_summary": {
            "suitability": rule_evaluation["suitability"],
            "suitability_kn": rule_evaluation["suitability_kn"],
            "remaining_days": rule_evaluation["remaining_days"],
            "estimated_deadline": rule_evaluation["estimated_deadline"],
            "risks": rule_evaluation["risks"],
        }
    }
