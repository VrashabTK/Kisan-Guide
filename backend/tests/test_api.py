import asyncio
import time
from backend.app.schemas import (
    CropRecommendationRequest,
    StorageRecommendationRequest,
    WeatherAdvisoryRequest,
    SavedItemCreate,
    UserProfileUpdate
)
from backend.app.api.routes.crops import get_crop_recommendation
from backend.app.api.routes.weather import get_current_weather, get_weather_forecast, get_weather_advisory
from backend.app.api.routes.storage import get_storage_recommendation
from backend.app.api.routes.saved import create_saved_item, list_saved_items, remove_saved_item
from backend.app.api.routes.auth import get_my_profile, update_my_profile
import backend.app.services.weather_service as ws

def setup_weather_cache():
    now = time.time()
    test_weather = {
        "taluk": "Bantwal",
        "taluk_kn": "ಬಂಟ್ವಾಳ",
        "zone": "Midland / River Valley",
        "latitude": 12.8946,
        "longitude": 75.0345,
        "current": {
            "temperature": 28.5,
            "feels_like": 31.0,
            "humidity": 75.0,
            "rainfall": 0.0,
            "wind_speed": 12.0,
            "wind_direction": 250.0,
            "cloud_cover": 40.0,
            "pressure": 1010.0,
            "condition_en": "Partly cloudy",
            "condition_kn": "ಭಾಗಶಃ ಮೋಡ",
            "weather_code": 2,
        },
        "hourly_forecast": [],
        "daily_forecast": [],
        "alerts": [],
        "fetched_at": int(now),
        "source": "Open-Meteo Verified Test Feed",
    }
    for tlk in [
        "Mangaluru", "Bantwal", "Belthangady", "Puttur",
        "Sullia", "Moodbidri", "Kadaba", "Mulki", "Ullal"
    ]:
        p = dict(test_weather)
        p["taluk"] = tlk
        ws._CACHE[tlk] = (now, p)

# Seed cache for test suite
setup_weather_cache()

def test_crop_recommendation_endpoint():
    setup_weather_cache()
    req = CropRecommendationRequest(
        taluk="Bantwal",
        water_availability="Moderate",
        soil_type="Laterite",
        irrigation_available=True
    )
    res = asyncio.run(get_crop_recommendation(req, uid="test_uid_01"))
    assert res["taluk"] == "Bantwal"
    assert "primary_recommendation" in res
    assert len(res["all_recommendations"]) == 4

def test_weather_endpoints():
    setup_weather_cache()
    cur = asyncio.run(get_current_weather("Bantwal"))
    assert cur["taluk"] == "Bantwal"
    assert "temperature" in cur["current"]

    fc = asyncio.run(get_weather_forecast("Bantwal"))
    assert fc["taluk"] == "Bantwal"

    adv_req = WeatherAdvisoryRequest(taluk="Bantwal", crop="Arecanut")
    adv = asyncio.run(get_weather_advisory(adv_req))
    assert "advisories" in adv
    assert len(adv["advisories"]) > 0

def test_storage_recommendation_endpoint():
    setup_weather_cache()
    req = StorageRecommendationRequest(
        crop="Coconut",
        harvest_date="2026-11-01",
        storage_method="Ventilated room",
        crop_condition="Dry",
        taluk="Mangaluru"
    )
    res = asyncio.run(get_storage_recommendation(req, uid="test_uid_01"))
    assert res["crop"] == "Coconut"
    assert res["suitability"] == "Suitable"
    assert "remaining_days" in res
    assert len(res["instructions_en"]) > 0

def test_saved_items_authenticated_flow():
    test_uid = "farmer_test_888"
    item_payload = SavedItemCreate(
        itemType="Crop Recommendation",
        itemId="rec_test_101",
        title="Coconut in Mangaluru",
        title_kn="ಮಂಗಳೂರಿನಲ್ಲಿ ತೆಂಗು",
        crop="Coconut",
        location="Mangaluru",
        content={"suitability": 95}
    )
    # 1. Create
    saved = asyncio.run(create_saved_item(item_payload, uid=test_uid))
    assert saved["savedItemId"] is not None
    saved_id = saved["savedItemId"]

    # 2. List
    items = asyncio.run(list_saved_items(category=None, uid=test_uid))
    assert any(i["savedItemId"] == saved_id for i in items)

    # 3. Remove
    del_res = asyncio.run(remove_saved_item(saved_id, uid=test_uid))
    assert del_res["success"] is True

def test_profile_update_flow():
    test_uid = "farmer_profile_test_1"
    claims = {"uid": test_uid, "name": "Venkatesh Rao", "email": "venky@dk.in"}
    profile = asyncio.run(get_my_profile(claims))
    assert profile["uid"] == test_uid

    update_payload = UserProfileUpdate(
        fullName="Venkatesh Rao Updated",
        taluk="Belthangady",
        primaryCrops=["Arecanut", "Cocoa"]
    )
    updated = asyncio.run(update_my_profile(update_payload, uid=test_uid))
    assert updated["fullName"] == "Venkatesh Rao Updated"
    assert updated["taluk"] == "Belthangady"
