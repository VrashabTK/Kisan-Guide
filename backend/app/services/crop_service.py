"""
Crop Recommendation Service for Dakshina Kannada.
Evaluates soil, seasonal calendar, water availability, and live local weather.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from backend.app.services.weather_service import get_weather
from backend.app.agricultural_rules.crops import evaluate_crop_suitability, DK_TALUKS, SUPPORTED_CROPS

async def recommend_crops(
    taluk: str,
    water_availability: str,
    soil_type: Optional[str] = None,
    irrigation_available: Optional[bool] = None,
    previous_crop: Optional[str] = None,
    plantation_area_acres: Optional[float] = None,
) -> Dict[str, Any]:
    # 1. Fetch current weather snapshot for taluk
    weather_data = await get_weather(taluk)
    current_weather = weather_data.get("current", {})
    daily_forecast = weather_data.get("daily_forecast", [])
    
    current_temp = current_weather.get("temperature", 28.0)
    current_humidity = current_weather.get("humidity", 75.0)
    
    # Calculate 4-day rainfall forecast sum
    forecast_rain_sum = sum(d.get("rainfall_sum", 0.0) for d in daily_forecast) if daily_forecast else 0.0
    
    current_month = datetime.utcnow().month

    # 2. Evaluate crop suitability
    evaluation = evaluate_crop_suitability(
        taluk=taluk,
        water_availability=water_availability,
        current_temp=current_temp,
        current_humidity=current_humidity,
        rainfall_forecast_mm=forecast_rain_sum,
        current_month=current_month,
        soil_type=soil_type,
        irrigation_available=irrigation_available,
    )

    # Attach live weather snapshot
    evaluation["weather_snapshot"] = {
        "temperature": current_temp,
        "humidity": current_humidity,
        "rainfall_forecast_4d_mm": round(forecast_rain_sum, 1),
        "condition_en": current_weather.get("condition_en", "Normal"),
        "condition_kn": current_weather.get("condition_kn", "ಸಾಧಾರಣ"),
    }
    evaluation["water_availability_input"] = water_availability
    evaluation["optional_inputs"] = {
        "soil_type": soil_type,
        "irrigation_available": irrigation_available,
        "previous_crop": previous_crop,
        "plantation_area_acres": plantation_area_acres,
    }

    return evaluation
