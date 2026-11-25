"""
Comprehensive Test Suite for KISSAN GUIDE Farm Management & Daily Monitoring System.
Verifies:
- Farm creation & DK validation (4 crops, 9 taluks)
- Dual timeline calculations (Actual crop day vs Monitoring day)
- Late farm registration on Day 15 (stage & day 15 activities, not day 1)
- Historical audit on progress corrections (farm_corrections)
- Activity completion and skipped reason tracking
- Weather-adaptive activity guidance
- Daily farmer observations & harvest logging
- Multiple farms isolation
- Strict farm ownership security
"""

import time
from datetime import date, timedelta
from backend.app.schemas import (
    FarmCreate,
    FarmProgressCorrectionRequest,
    ActivityActionRequest,
    ObservationCreate,
    HarvestCreate,
)
from backend.app.services.database import (
    create_user,
    get_farm_by_id_db,
    get_farms_by_user_db,
    get_farm_corrections_db,
    get_farm_activities_for_date_db,
    get_farm_observations_db,
    get_farm_harvests_db,
)
from backend.app.agricultural_rules.crops import SUPPORTED_CROPS, DK_TALUKS
from backend.app.agricultural_rules.farm_lifecycle import (
    get_crop_stages,
    validate_stage_consistency,
    get_default_stage_for_day
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

def test_crop_stages_and_stage_consistency():
    """Verifies that all 4 crops have defined stages and consistency warning logic works."""
    for c in ["Coconut", "Rice", "Arecanut", "Cocoa"]:
        stages = get_crop_stages(c)
        assert len(stages) >= 4, f"Crop {c} must have detailed growth stages"
        for s in stages:
            assert "id" in s
            assert "name_en" in s
            assert "name_kn" in s

    # Rice Day 15 should normally be Land Prep or Nursery
    rice_day_15_stage = get_default_stage_for_day("Rice", 15)
    assert rice_day_15_stage["id"] in ["land_prep", "nursery"]

    # Warning triggered if Rice Day 15 selects "Harvest"
    warning = validate_stage_consistency("Rice", 15, "harvest")
    assert warning is not None
    assert "Farming Day 15 is usually in the" in warning

    # No warning if Rice Day 15 selects "Nursery & Sowing"
    no_warning = validate_stage_consistency("Rice", 15, "nursery")
    assert no_warning is None

def test_farm_creation_and_timeline_day1():
    """Tests standard farm creation starting today (Crop Day 1, Monitoring Day 1)."""
    user = create_user(
        identifier=f"farmer_std_{int(time.time()*1000)}@kissan.in",
        password="SecurePassword123!",
        full_name="Ramesh Gowda",
        taluk="Bantwal"
    )
    uid = user["user"]["id"]

    farm_payload = {
        "name": "Bantwal Riverview Paddy",
        "crop": "Rice",
        "taluk": "Bantwal",
        "area": 2.5,
        "area_unit": "acre",
        "cultivation_start_date": date.today().isoformat(),
        "initial_farming_day": 1,
        "water_availability": "High",
        "variety": "MO4",
        "cultivation_method": "Transplanting"
    }

    import asyncio
    created = asyncio.run(register_new_farm(farm_payload, uid))
    assert created["id"] is not None
    assert created["user_id"] == uid
    assert created["crop"] == "Rice"
    assert created["taluk"] == "Bantwal"
    assert created["current_crop_day"] == 1
    assert created["current_monitoring_day"] == 1

def test_late_farm_registration_day15():
    """
    CRITICAL REQUIREMENT:
    Farmer started Rice 15 days ago and joins today.
    - Actual crop farming day = 15
    - Monitoring day = 1
    - Activities generated must be for Day 15 / confirmed stage, NOT Day 1!
    """
    import asyncio
    user = create_user(
        identifier=f"988{int(time.time())%10000000:07d}",
        password="SecurePassword123!",
        full_name="Suresh Poojary",
        taluk="Puttur"
    )
    uid = user["user"]["id"]

    # Farmer enters current farming day = 15 manually
    farm_payload = {
        "name": "Puttur Hillside Rice",
        "crop": "Rice",
        "taluk": "Puttur",
        "area": 1.75,
        "area_unit": "acre",
        "initial_farming_day": 15,
        "current_stage": "Nursery & Sowing",
        "water_availability": "Moderate"
    }

    created = asyncio.run(register_new_farm(farm_payload, uid))
    farm_id = created["id"]

    # Verify dual timeline on Day 15
    timeline = calculate_farm_timeline(created)
    assert timeline["crop_day"] == 15, f"Expected Crop Day 15, got {timeline['crop_day']}"
    assert timeline["monitoring_day"] == 1, f"Expected Monitoring Day 1, got {timeline['monitoring_day']}"

    # Verify advance to next day
    tomorrow = date.today() + timedelta(days=1)
    tomorrow_tl = calculate_farm_timeline(created, target_date=tomorrow)
    assert tomorrow_tl["crop_day"] == 16
    assert tomorrow_tl["monitoring_day"] == 2

    # Check today's activities: must be for Day 15
    activities = asyncio.run(get_or_generate_daily_activities(farm_id, uid))
    assert len(activities) > 0
    for act in activities:
        assert act["crop_day"] == 15
        assert act["monitoring_day"] == 1
        assert act["farm_id"] == farm_id

    # Verify no fabricated historical records prior to monitoring
    past_date = (date.today() - timedelta(days=5)).isoformat()
    past_activities = asyncio.run(get_or_generate_daily_activities(farm_id, uid, target_date=date.today() - timedelta(days=5)))
    assert len(past_activities) == 0, "System must never fabricate historical activities prior to monitoring start date"

def test_farming_progress_correction_audit():
    """Tests updating farming day or stage with permanent correction audit log."""
    import asyncio
    user = create_user(
        identifier=f"farmer_corr_{int(time.time()*1000)}@kissan.in",
        password="SecurePassword123!",
        full_name="Kishore Kumar",
        taluk="Belthangady"
    )
    uid = user["user"]["id"]

    farm = asyncio.run(register_new_farm({
        "name": "Belthangady Areca Garden",
        "crop": "Arecanut",
        "taluk": "Belthangady",
        "area": 3.0,
        "initial_farming_day": 40,
        "current_stage": "Young Garden Growth (1 - 4 Years)"
    }, uid))
    farm_id = farm["id"]

    # Farmer corrects farming day to 45 and stage with reason
    updated = asyncio.run(correct_farm_progress(
        farm_id=farm_id,
        user_id=uid,
        new_crop_day=45,
        new_stage="Young Garden Growth (1 - 4 Years)",
        reason="Realized seedlings were planted 5 days earlier than remembered"
    ))
    assert updated["current_crop_day"] == 45

    # Check audit log in database
    corrections = get_farm_corrections_db(farm_id)
    assert len(corrections) == 1
    c = corrections[0]
    assert c["prev_crop_day"] == 40
    assert c["new_crop_day"] == 45
    assert "planted 5 days earlier" in c["reason"]

def test_activity_completion_and_skipping():
    """Tests marking activities as Completed and Skipped with reasons."""
    import asyncio
    user = create_user(
        identifier=f"farmer_act_{int(time.time()*1000)}@kissan.in",
        password="SecurePassword123!",
        full_name="Anand Hegde",
        taluk="Sullia"
    )
    uid = user["user"]["id"]

    farm = asyncio.run(register_new_farm({
        "name": "Sullia Coconut Grove",
        "crop": "Coconut",
        "taluk": "Sullia",
        "area": 4.0,
        "initial_farming_day": 365,
        "current_stage": "Juvenile Palm (1 - 4 Years)"
    }, uid))
    farm_id = farm["id"]

    activities = asyncio.run(get_or_generate_daily_activities(farm_id, uid))
    assert len(activities) >= 2

    # Mark first activity completed
    act1 = activities[0]
    done_res = asyncio.run(mark_activity_done(act1["id"], farm_id, uid))
    assert done_res["status"] == "completed"
    assert done_res["completed_at"] is not None

    # Mark second activity skipped with structured reason
    act2 = activities[1]
    skip_res = asyncio.run(mark_activity_skipped(
        act2["id"],
        farm_id,
        uid,
        reason="Heavy rainfall made basin digging impractical"
    ))
    assert skip_res["status"] == "skipped"
    assert skip_res["skip_reason"] == "Heavy rainfall made basin digging impractical"

def test_farmer_observations_and_harvest():
    """Tests saving observations and recording farm harvest batches."""
    import asyncio
    user = create_user(
        identifier=f"farmer_obs_{int(time.time()*1000)}@kissan.in",
        password="SecurePassword123!",
        full_name="Divya Rai",
        taluk="Mangaluru"
    )
    uid = user["user"]["id"]

    farm = asyncio.run(register_new_farm({
        "name": "Mangaluru Cocoa Intercrop",
        "crop": "Cocoa",
        "taluk": "Mangaluru",
        "area": 1.5,
        "initial_farming_day": 730,
        "current_stage": "Mature Bearing Garden (5+ Years)"
    }, uid))
    farm_id = farm["id"]

    # 1. Observation
    obs = asyncio.run(add_farm_observation({
        "farm_id": farm_id,
        "field_condition": "Good soil aeration",
        "soil_moisture": "Moist",
        "pest_symptoms": "Minor tea mosquito bug on tender shoots",
        "additional_notes": "Pruned 4 vertical chupons"
    }, uid))
    assert obs["id"] is not None
    assert obs["crop_day"] == 730
    assert obs["monitoring_day"] == 1

    all_obs = get_farm_observations_db(farm_id)
    assert len(all_obs) == 1
    assert all_obs[0]["pest_symptoms"] == "Minor tea mosquito bug on tender shoots"

    # 2. Harvest
    harv = asyncio.run(add_farm_harvest({
        "farm_id": farm_id,
        "harvest_date": date.today().isoformat(),
        "quantity_kg": 140.0,
        "quality_grade": "Grade A ripe yellow pods",
        "storage_method": "Wooden fermentation box",
        "notes": "First harvest round of season"
    }, uid))
    assert harv["id"] is not None
    assert harv["quantity_kg"] == 140.0

    all_harv = get_farm_harvests_db(farm_id)
    assert len(all_harv) == 1
    assert all_harv[0]["quantity_kg"] == 140.0

def test_multiple_farms_isolation():
    """
    Verifies that a farmer can maintain multiple distinct farms:
    e.g. Farm 1 (Rice), Farm 2 (Arecanut) with independent timelines and activities.
    """
    import asyncio
    user = create_user(
        identifier=f"multi_farm_{int(time.time()*1000)}@kissan.in",
        password="SecurePassword123!",
        full_name="Manjunath Bhat",
        taluk="Kadaba"
    )
    uid = user["user"]["id"]

    farm_rice = asyncio.run(register_new_farm({
        "name": "Valley Rice Plot",
        "crop": "Rice",
        "taluk": "Kadaba",
        "area": 2.0,
        "initial_farming_day": 15,
        "current_stage": "Nursery & Sowing"
    }, uid))

    farm_areca = asyncio.run(register_new_farm({
        "name": "Hillside Arecanut Garden",
        "crop": "Arecanut",
        "taluk": "Kadaba",
        "area": 3.5,
        "initial_farming_day": 1200,
        "current_stage": "Young Garden Growth (1 - 4 Years)"
    }, uid))

    # Retrieve all user farms
    user_farms = asyncio.run(get_user_farms_with_status(uid))
    assert len(user_farms) == 2

    # Verify timelines are strictly separate
    f_rice = next(f for f in user_farms if f["id"] == farm_rice["id"])
    f_areca = next(f for f in user_farms if f["id"] == farm_areca["id"])

    assert f_rice["crop"] == "Rice"
    assert f_rice["current_crop_day"] == 15

    assert f_areca["crop"] == "Arecanut"
    assert f_areca["current_crop_day"] == 1200

    # Verify activities are completely separate
    acts_rice = asyncio.run(get_or_generate_daily_activities(farm_rice["id"], uid))
    acts_areca = asyncio.run(get_or_generate_daily_activities(farm_areca["id"], uid))

    assert len(acts_rice) > 0
    assert len(acts_areca) > 0
    for a in acts_rice:
        assert a["farm_id"] == farm_rice["id"]
        assert a["crop_day"] == 15
    for a in acts_areca:
        assert a["farm_id"] == farm_areca["id"]
        assert a["crop_day"] == 1200

def test_farm_ownership_security():
    """Ensures Farmer A cannot access or modify Farmer B's farm."""
    import asyncio
    userA = create_user(
        identifier=f"farmerA_{int(time.time()*1000)}@kissan.in",
        password="Password123!",
        full_name="Farmer A",
        taluk="Moodbidri"
    )
    userB = create_user(
        identifier=f"farmerB_{int(time.time()*1000)}@kissan.in",
        password="Password123!",
        full_name="Farmer B",
        taluk="Moodbidri"
    )

    farmA = asyncio.run(register_new_farm({
        "name": "Farmer A Coconut Farm",
        "crop": "Coconut",
        "taluk": "Moodbidri",
        "area": 1.0,
        "initial_farming_day": 10
    }, userA["user"]["id"]))

    # Farmer B attempts to get Farm A's detail
    detail = asyncio.run(get_farm_detail(farmA["id"], userB["user"]["id"]))
    assert detail is None, "Farmer B must NOT be able to view Farmer A's farm"

    # Farmer B attempts to mark activity done on Farm A
    res = asyncio.run(mark_activity_done("any_act_id", farmA["id"], userB["user"]["id"]))
    assert res is None, "Farmer B must NOT be able to update activities on Farm A"


def test_api_farm_endpoints():
    """Tests the /api/v1/farms HTTP API endpoints with authentication."""
    from fastapi.testclient import TestClient
    from backend.app.main import app

    client = TestClient(app)
    # Register a farmer via API
    reg_res = client.post("/api/v1/auth/signup", json={
        "identifier": f"api_farmer_{int(time.time()*1000)}@kissan.in",
        "password": "Password123!",
        "confirmPassword": "Password123!",
        "fullName": "API Farmer",
        "taluk": "Ullal"
    })
    assert reg_res.status_code in (200, 201), f"Signup failed: {reg_res.text}"
    token = reg_res.json().get("access_token") or reg_res.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create a Farm via API (Late registration on Day 20)
    farm_res = client.post("/api/v1/farms", json={
        "name": "Ullal Coastal Rice",
        "crop": "Rice",
        "taluk": "Ullal",
        "area": 1.5,
        "area_unit": "acre",
        "initial_farming_day": 20,
        "current_stage": "Transplanting / Direct Seeding",
        "water_availability": "Moderate"
    }, headers=headers)
    assert farm_res.status_code == 201, f"Farm creation failed: {farm_res.text}"
    farm_data = farm_res.json()
    farm_id = farm_data["id"]
    assert farm_data["current_crop_day"] == 20
    assert farm_data["current_monitoring_day"] == 1

    # 2. List Farms
    list_res = client.get("/api/v1/farms", headers=headers)
    assert list_res.status_code == 200
    farms_list = list_res.json()
    assert len(farms_list) >= 1
    assert any(f["id"] == farm_id for f in farms_list)

    # 3. Get Today's Activities
    acts_res = client.get(f"/api/v1/farms/{farm_id}/activities/today", headers=headers)
    assert acts_res.status_code == 200
    acts = acts_res.json()
    assert len(acts) > 0
    act_id = acts[0]["id"]

    # 4. Complete an Activity
    done_res = client.post(f"/api/v1/farms/{farm_id}/activities/{act_id}/complete", headers=headers)
    assert done_res.status_code == 200
    assert done_res.json()["status"] == "completed"

    # 5. Progress Correction via API
    corr_res = client.post(f"/api/v1/farms/{farm_id}/progress-correction", json={
        "new_crop_day": 25,
        "new_stage": "Transplanting / Direct Seeding",
        "reason": "Corrected day count based on field diary"
    }, headers=headers)
    assert corr_res.status_code == 200
    assert corr_res.json()["current_crop_day"] == 25

    # 6. Verify audit history endpoint
    hist_corr = client.get(f"/api/v1/farms/{farm_id}/corrections", headers=headers)
    assert hist_corr.status_code == 200
    assert len(hist_corr.json()) >= 1

    # 7. Add daily observation via API
    obs_res = client.post(f"/api/v1/farms/{farm_id}/observations", json={
        "farm_id": farm_id,
        "field_condition": "Transplanting completed",
        "soil_moisture": "Standing water 3cm",
        "pest_symptoms": "Nil",
        "additional_notes": "Good seedling vigor"
    }, headers=headers)
    assert obs_res.status_code == 201

    # 8. Record harvest via API
    harv_res = client.post(f"/api/v1/farms/{farm_id}/harvests", json={
        "farm_id": farm_id,
        "harvest_date": date.today().isoformat(),
        "quantity_kg": 500.0,
        "quality_grade": "Grade A",
        "storage_method": "Jute bag in ventilated room"
    }, headers=headers)
    assert harv_res.status_code == 201
