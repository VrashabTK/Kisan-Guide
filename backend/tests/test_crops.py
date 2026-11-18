# Crop tests for Dakshina Kannada
from backend.app.agricultural_rules.crops import (
    evaluate_crop_suitability,
    DK_TALUKS,
    SUPPORTED_CROPS,
    CROP_PROFILES
)

def test_dakshina_kannada_taluks():
    assert len(DK_TALUKS) == 9
    expected_taluks = [
        "Mangaluru", "Bantwal", "Belthangady", "Puttur",
        "Sullia", "Moodbidri", "Kadaba", "Mulki", "Ullal"
    ]
    for taluk in expected_taluks:
        assert taluk in DK_TALUKS
        assert "lat" in DK_TALUKS[taluk]
        assert "lon" in DK_TALUKS[taluk]
        assert "name_kn" in DK_TALUKS[taluk]

def test_supported_crops_scope():
    assert set(SUPPORTED_CROPS) == {"Coconut", "Rice", "Arecanut", "Cocoa"}
    for crop in SUPPORTED_CROPS:
        assert crop in CROP_PROFILES
        profile = CROP_PROFILES[crop]
        assert "optimal_temp_range" in profile
        assert "water_requirement" in profile
        assert "precautions_en" in profile
        assert "precautions_kn" in profile

def test_high_water_rice_recommendation():
    # Rice requires High water availability
    eval_result = evaluate_crop_suitability(
        taluk="Mangaluru",
        water_availability="High",
        current_temp=28.0,
        current_humidity=80.0,
        rainfall_forecast_mm=120.0,
        current_month=6, # Kharif season
    )
    assert eval_result["taluk"] == "Mangaluru"
    assert "primary_recommendation" in eval_result
    all_recs = {r["crop"]: r["suitability_score"] for r in eval_result["all_recommendations"]}
    
    # Rice should score very high under High water and monsoon June
    assert all_recs["Rice"] >= 80

def test_low_water_penalizes_rice():
    # With Low water, Rice should score lower than Coconut or Arecanut
    eval_result = evaluate_crop_suitability(
        taluk="Puttur",
        water_availability="Low",
        current_temp=29.0,
        current_humidity=65.0,
        rainfall_forecast_mm=5.0,
        current_month=2,
    )
    all_recs = {r["crop"]: r["suitability_score"] for r in eval_result["all_recommendations"]}
    assert all_recs["Rice"] < all_recs["Coconut"]
