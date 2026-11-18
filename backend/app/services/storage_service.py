"""
Crop Storage Assistant Service for Dakshina Kannada.
Analyzes post-harvest duration, storage method, crop condition, and ambient humidity.
"""

from typing import Dict, Any, Optional
from backend.app.services.weather_service import get_weather
from backend.app.agricultural_rules.storage import evaluate_storage_practice
from backend.app.agricultural_rules.crops import SUPPORTED_CROPS

async def recommend_storage_practices(
    crop: str,
    harvest_date: str,
    storage_method: str,
    crop_condition: str,
    taluk: str = "Mangaluru",
    quantity_kg: Optional[float] = None,
    storage_facility_description: Optional[str] = None,
) -> Dict[str, Any]:
    # 1. Fetch current weather for the taluk to obtain ambient temperature and humidity
    weather_data = await get_weather(taluk)
    current_weather = weather_data.get("current", {})
    ambient_temp = current_weather.get("temperature", 28.0)
    ambient_humidity = current_weather.get("humidity", 75.0)

    # 2. Evaluate storage practice
    evaluation = evaluate_storage_practice(
        crop=crop,
        harvest_date=harvest_date,
        storage_method=storage_method,
        crop_condition=crop_condition,
        ambient_temp=ambient_temp,
        ambient_humidity=ambient_humidity,
        quantity_kg=quantity_kg or 0.0,
    )

    evaluation["taluk"] = taluk
    evaluation["taluk_kn"] = weather_data.get("taluk_kn", taluk)
    evaluation["ambient_weather"] = {
        "temperature": ambient_temp,
        "humidity": ambient_humidity,
        "condition_en": current_weather.get("condition_en", ""),
        "condition_kn": current_weather.get("condition_kn", ""),
    }
    evaluation["optional_inputs"] = {
        "quantity_kg": quantity_kg,
        "storage_facility_description": storage_facility_description,
    }

    return evaluation
