from fastapi import APIRouter, Query, Depends
from typing import Optional, Dict, Any, List
from backend.app.services.weather_service import get_weather
from backend.app.agricultural_rules.advisories import generate_farming_advisories
from backend.app.schemas import WeatherAdvisoryRequest

router = APIRouter(prefix="/weather", tags=["Weather Assistant"])

@router.get("/current")
async def get_current_weather(
    taluk: str = Query("Mangaluru", description="Taluk in Dakshina Kannada")
):
    weather_data = await get_weather(taluk)
    return {
        "taluk": weather_data["taluk"],
        "taluk_kn": weather_data["taluk_kn"],
        "zone": weather_data["zone"],
        "current": weather_data["current"],
        "fetched_at": weather_data["fetched_at"],
        "source": weather_data["source"],
    }

@router.get("/forecast")
async def get_weather_forecast(
    taluk: str = Query("Mangaluru", description="Taluk in Dakshina Kannada")
):
    weather_data = await get_weather(taluk)
    return {
        "taluk": weather_data["taluk"],
        "taluk_kn": weather_data["taluk_kn"],
        "current": weather_data["current"],
        "hourly_forecast": weather_data["hourly_forecast"],
        "daily_forecast": weather_data["daily_forecast"],
        "alerts": weather_data["alerts"],
        "source": weather_data["source"],
    }

@router.post("/advisory")
async def get_weather_advisory(
    req: WeatherAdvisoryRequest
):
    weather_data = await get_weather(req.taluk)
    advisories = generate_farming_advisories(
        weather_summary=weather_data.get("current", {}),
        selected_crop=req.crop or "All",
        forecast_days=weather_data.get("daily_forecast", [])
    )
    return {
        "taluk": req.taluk,
        "taluk_kn": weather_data.get("taluk_kn", req.taluk),
        "crop": req.crop,
        "advisories": advisories,
        "weather_summary": weather_data.get("current", {}),
    }

@router.get("/alerts")
async def get_weather_alerts(
    taluk: str = Query("Mangaluru", description="Taluk in Dakshina Kannada")
):
    weather_data = await get_weather(taluk)
    return {
        "taluk": weather_data["taluk"],
        "taluk_kn": weather_data["taluk_kn"],
        "alerts": weather_data["alerts"],
        "count": len(weather_data["alerts"]),
        "source": weather_data["source"],
    }

@router.get("/alerts/history")
async def get_alerts_history(
    taluk: str = Query("Mangaluru", description="Taluk in Dakshina Kannada")
):
    # Returns recent alerts snapshot
    weather_data = await get_weather(taluk)
    return weather_data["alerts"]
