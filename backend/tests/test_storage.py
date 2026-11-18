# Storage tests for Dakshina Kannada crops
from datetime import datetime, timedelta
from backend.app.agricultural_rules.storage import (
    evaluate_storage_practice,
    STORAGE_PROFILES,
    STORAGE_METHODS,
    CROP_CONDITIONS
)

def test_storage_profiles_complete():
    for crop in ["Coconut", "Rice", "Arecanut", "Cocoa"]:
        assert crop in STORAGE_PROFILES
        p = STORAGE_PROFILES[crop]
        assert "optimal_methods" in p
        assert "unsuitable_methods" in p
        assert "base_duration_days" in p
        assert "guidelines_en" in p
        assert "guidelines_kn" in p

def test_suitable_arecanut_storage():
    today = datetime.utcnow().date()
    harvest_date = str(today - timedelta(days=10))

    result = evaluate_storage_practice(
        crop="Arecanut",
        harvest_date=harvest_date,
        storage_method="Jute bag",
        crop_condition="Dry",
        ambient_temp=26.0,
        ambient_humidity=65.0
    )

    assert result["suitability"] == "Suitable"
    assert result["days_elapsed"] == 10
    assert result["remaining_days"] > 0
    assert result["risks"]["moisture"] == "Low"
    assert result["risks"]["spoilage"] == "Low"
    assert "instructions_en" in result
    assert "instructions_kn" in result

def test_unsuitable_closed_container_penalized():
    today = datetime.utcnow().date()
    harvest_date = str(today - timedelta(days=2))

    # Closed container is unsuitable for fresh produce like Cocoa / Coconut
    result = evaluate_storage_practice(
        crop="Cocoa",
        harvest_date=harvest_date,
        storage_method="Closed container",
        crop_condition="Fresh",
        ambient_temp=28.0,
        ambient_humidity=75.0
    )

    assert result["suitability"] == "Not Recommended"
    assert result["risks"]["spoilage"] == "High"
    # Safe duration is severely curtailed
    assert result["estimated_duration_days"] < 10
