"""
Farm Management & Monitoring Service for KISSAN GUIDE.
Handles timeline computation (actual crop day vs monitoring day),
intelligent daily activity generation, weather-adaptive recommendations,
and farm lifecycle tracking.
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
import logging

from backend.app.agricultural_rules.farm_lifecycle import (
    CROP_STAGES,
    CROP_ACTIVITIES_KNOWLEDGE_BASE,
    get_crop_stages,
    get_default_stage_for_day,
    validate_stage_consistency
)
from backend.app.services.weather_service import get_weather
from backend.app.services.database import (
    create_farm_db,
    get_farms_by_user_db,
    get_farm_by_id_db,
    update_farm_db,
    delete_farm_db,
    create_farm_correction_db,
    get_farm_corrections_db,
    save_farm_activities_db,
    get_farm_activities_for_date_db,
    get_farm_activities_history_db,
    update_farm_activity_status_db,
    create_farm_observation_db,
    get_farm_observations_db,
    create_farm_harvest_db,
    get_farm_harvests_db,
)

logger = logging.getLogger("kissan_guide.farm_service")

# ==================== Timeline Calculations ====================

def calculate_farm_timeline(farm: Dict[str, Any], target_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Computes two distinct timelines:
    1. Actual crop farming day (how long the crop has been cultivated)
    2. KISSAN GUIDE monitoring day (how long farmer has tracked it in the app)
    """
    if target_date is None:
        target_date = date.today()

    mon_start_str = farm.get("monitoring_start_date") or date.today().isoformat()
    try:
        mon_start = date.fromisoformat(mon_start_str)
    except Exception:
        mon_start = date.today()

    # Monitoring day calculation
    mon_days = (target_date - mon_start).days + 1
    monitoring_day = max(1, mon_days)

    # Actual crop farming day calculation
    cult_start_str = farm.get("cultivation_start_date")
    initial_farming_day = int(farm.get("initial_farming_day") or 1)

    if cult_start_str:
        try:
            cult_start = date.fromisoformat(cult_start_str)
            crop_day = (target_date - cult_start).days + 1
            crop_day = max(1, crop_day)
        except Exception:
            crop_day = max(1, initial_farming_day + (target_date - mon_start).days)
    else:
        # Farmer joined late and gave current farming day without start date
        crop_day = max(1, initial_farming_day + (target_date - mon_start).days)

    return {
        "crop_day": crop_day,
        "monitoring_day": monitoring_day,
        "target_date": target_date.isoformat(),
        "is_prior_to_monitoring": target_date < mon_start
    }

# ==================== Farm Lifecycle & Creation ====================

async def register_new_farm(farm_payload: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Registers a new farm in persistent database, calculates timeline,
    and automatically initializes the first batch of daily activities.
    """
    today_str = date.today().isoformat()
    crop = farm_payload["crop"]
    
    # Handle Late Registration Day vs Start Date
    cult_start = farm_payload.get("cultivation_start_date")
    initial_day = int(farm_payload.get("initial_farming_day") or 1)

    if cult_start:
        try:
            c_date = date.fromisoformat(cult_start)
            calculated_initial_day = max(1, (date.today() - c_date).days + 1)
            initial_day = calculated_initial_day
        except Exception:
            pass

    # Stage determination / confirmation
    user_stage = farm_payload.get("current_stage")
    if not user_stage:
        def_stage = get_default_stage_for_day(crop, initial_day)
        user_stage = def_stage.get("name_en", "Active Cultivation")

    farm_data = {
        "user_id": user_id,
        "name": farm_payload.get("name") or f"{crop} Farm ({farm_payload['taluk']})",
        "crop": crop,
        "taluk": farm_payload["taluk"],
        "area": float(farm_payload["area"]),
        "area_unit": farm_payload.get("area_unit", "acre"),
        "cultivation_start_date": cult_start,
        "initial_farming_day": initial_day,
        "monitoring_start_date": today_str,
        "current_stage": user_stage,
        "variety": farm_payload.get("variety"),
        "cultivation_method": farm_payload.get("cultivation_method"),
        "soil_type": farm_payload.get("soil_type"),
        "water_availability": farm_payload.get("water_availability", "Moderate"),
        "notes": farm_payload.get("notes")
    }

    created = create_farm_db(farm_data)

    # Pre-generate today's activities immediately
    await get_or_generate_daily_activities(created["id"], user_id)

    # Attach computed timeline to return object
    timeline = calculate_farm_timeline(created)
    created["current_crop_day"] = timeline["crop_day"]
    created["current_monitoring_day"] = timeline["monitoring_day"]

    return created

async def get_user_farms_with_status(user_id: str) -> List[Dict[str, Any]]:
    """Retrieves all active farms for user with live timeline and pending task count."""
    farms = get_farms_by_user_db(user_id)
    today_str = date.today().isoformat()
    results = []

    for f in farms:
        timeline = calculate_farm_timeline(f)
        activities = get_farm_activities_for_date_db(f["id"], today_str)
        pending_count = sum(1 for a in activities if a["status"] == "pending")
        completed_count = sum(1 for a in activities if a["status"] == "completed")
        skipped_count = sum(1 for a in activities if a["status"] == "skipped")

        results.append({
            **f,
            "current_crop_day": timeline["crop_day"],
            "current_monitoring_day": timeline["monitoring_day"],
            "today_activities_count": len(activities),
            "today_pending_count": pending_count,
            "today_completed_count": completed_count,
            "today_skipped_count": skipped_count,
            "stages": get_crop_stages(f["crop"])
        })

    return results

async def get_farm_detail(farm_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves single farm with timeline, stages, and recent weather."""
    farm = get_farm_by_id_db(farm_id, user_id)
    if not farm:
        return None

    timeline = calculate_farm_timeline(farm)
    stages = get_crop_stages(farm["crop"])

    # Fetch live weather snapshot for farm taluk
    try:
        weather_data = await get_weather(farm["taluk"])
        current_weather = weather_data.get("current", {})
        weather_alerts = weather_data.get("alerts", [])
    except Exception as e:
        logger.debug(f"Weather fetch fallback for farm {farm_id}: {e}")
        current_weather = {}
        weather_alerts = []

    today_str = date.today().isoformat()
    today_acts = get_farm_activities_for_date_db(farm_id, today_str)

    return {
        **farm,
        "current_crop_day": timeline["crop_day"],
        "current_monitoring_day": timeline["monitoring_day"],
        "stages": stages,
        "weather_snapshot": current_weather,
        "weather_alerts": weather_alerts,
        "today_activities": today_acts,
        "today_pending_count": sum(1 for a in today_acts if a["status"] == "pending"),
        "today_completed_count": sum(1 for a in today_acts if a["status"] == "completed")
    }

# ==================== Intelligent Daily Activity Generation ====================

async def get_or_generate_daily_activities(
    farm_id: str,
    user_id: str,
    target_date: Optional[date] = None
) -> List[Dict[str, Any]]:
    """
    Retrieves or generates appropriate agricultural activities for a farm.
    Considers:
    - Crop and actual farming day
    - Confirmed cultivation stage
    - Past completed activities (do not repeat non-recurring tasks)
    - Past skipped activities (reschedule critical skipped tasks)
    - Current local weather conditions (rain, storm, extreme temperature)
    """
    farm = get_farm_by_id_db(farm_id, user_id)
    if not farm:
        return []

    if target_date is None:
        target_date = date.today()

    date_str = target_date.isoformat()

    # 1. Check if activities already generated and saved for this date
    existing = get_farm_activities_for_date_db(farm_id, date_str)
    if existing:
        return existing

    # If the requested date is prior to monitoring start date, return empty list
    # (Never fabricate historical records for late joiners)
    mon_start_str = farm.get("monitoring_start_date") or date.today().isoformat()
    if date_str < mon_start_str:
        return []

    timeline = calculate_farm_timeline(farm, target_date)
    crop_day = timeline["crop_day"]
    monitoring_day = timeline["monitoring_day"]
    crop = farm["crop"]
    stage = farm["current_stage"]

    # 2. Retrieve history of completed & skipped activities
    history = get_farm_activities_history_db(farm_id, limit=50)
    completed_titles = {h["title_en"] for h in history if h["status"] == "completed"}
    recently_skipped = [h for h in history if h["status"] == "skipped"]

    # 3. Retrieve live weather context
    try:
        w_data = await get_weather(farm["taluk"])
        cur_w = w_data.get("current", {})
        temp = cur_w.get("temperature", 28.0)
        rainfall = cur_w.get("rainfall", 0.0)
        wind_speed = cur_w.get("wind_speed", 12.0)
        condition_en = cur_w.get("condition_en", "Normal")
        alerts = w_data.get("alerts", [])
        has_heavy_rain = rainfall > 10.0 or any("Rain" in a.get("title_en", "") for a in alerts)
        has_thunderstorm = any("Thunderstorm" in a.get("title_en", "") for a in alerts)
        is_high_heat = temp >= 34.0
    except Exception:
        cur_w = {}
        rainfall = 0.0
        wind_speed = 10.0
        has_heavy_rain = False
        has_thunderstorm = False
        is_high_heat = False

    # 4. Select candidate templates for this crop
    templates = CROP_ACTIVITIES_KNOWLEDGE_BASE.get(crop, [])
    selected_activities = []

    for tmpl in templates:
        # Check day range or recurring nature
        day_range = tmpl.get("typical_day_range", (1, 99999))
        is_recurring = tmpl.get("is_recurring", False)
        in_day_window = day_range[0] <= crop_day <= day_range[1]

        # Stage matching: template belongs to this stage or "all"
        stage_match = (tmpl.get("stage_id") == "all") or (tmpl.get("stage_id") in stage.lower().replace(" ", "_"))

        # For non-recurring tasks, skip if already completed in the past
        if not is_recurring and tmpl["title_en"] in completed_titles:
            continue

        if in_day_window or stage_match or is_recurring:
            # Weather adaptation
            w_influence_en = "Standard agronomic conditions."
            w_influence_kn = "ಸಾಮಾನ್ಯ ಹವಾಮಾನ ಪರಿಸ್ಥಿತಿ."
            priority = tmpl.get("priority", "medium")

            if has_heavy_rain:
                if tmpl.get("weather_sensitivity") == "rain_sensitive":
                    if "Irrigation" in tmpl["title_en"] or "ನೀರು" in tmpl["title_kn"]:
                        w_influence_en = "HEAVY RAIN ADVISORY: Natural rainfall is sufficient. Postpone planned irrigation to prevent root suffocation."
                        w_influence_kn = "ಭಾರಿ ಮಳೆ ಮುನ್ಸೂಚನೆ: ನೈಸರ್ಗಿಕ ಮಳೆ ಸಾಕಷ್ಟಿದೆ. ಬೇರು ಕೊಳೆತ ತಡೆಯಲು ನೀರಾವರಿಯನ್ನು ಮುಂದೂಡಿ."
                        priority = "low"
                    elif "Spray" in tmpl["title_en"] or "Bordeaux" in tmpl["title_en"] or "ಸಿಂಪಡಣೆ" in tmpl["title_kn"]:
                        w_influence_en = "RAIN DELAY: High chance of precipitation will wash away chemical/fungicide solutions. Delay application until clear skies."
                        w_influence_kn = "ಮಳೆಯ ಎಚ್ಚರಿಕೆ: ಮಳೆ ಬರುವುದರಿಂದ ಔಷಧ ತೊಳೆದು ಹೋಗುತ್ತದೆ. ಬಿಸಿಲು ಬರುವವರೆಗೆ ಸಿಂಪಡಣೆಯನ್ನು ಮುಂದೂಡಿ."
                        priority = "medium"
                    elif "Drainage" in tmpl["title_en"] or "ಚರಂಡಿ" in tmpl["title_kn"]:
                        w_influence_en = "URGENT WEATHER ADVISORY: Heavy rainfall expected. Ensure field drainage channels are cleared immediately."
                        w_influence_kn = "ತುರ್ತು ಎಚ್ಚರಿಕೆ: ಭಾರಿ ಮಳೆಯ ಸಂಭವವಿದೆ. ನೀರು ನಿಲ್ಲದಂತೆ ತೋಟದ ಚರಂಡಿಗಳನ್ನು ತಕ್ಷಣವೇ ಸ್ವಚ್ಛಗೊಳಿಸಿ."
                        priority = "high"
            elif is_high_heat:
                if "Irrigation" in tmpl["title_en"] or "ತೇವಾಂಶ" in tmpl["title_kn"]:
                    w_influence_en = "HIGH TEMPERATURE ADVISORY: Carry out basin watering strictly in early morning or late evening. Maintain thick mulch cover."
                    w_influence_kn = "ಹೆಚ್ಚಿನ ತಾಪಮಾನ: ಬಿಸಿಲು ಹೆಚ್ಚಿರುವುದರಿಂದ ಮುಂಜಾನೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ನೀರುಣಿಸಿ. ಬುಡಕ್ಕೆ ದಪ್ಪನೆಯ ಹೊದಿಕೆ ಹಾಕಿ."
                    priority = "high"
            elif wind_speed > 30.0 or has_thunderstorm:
                w_influence_en = "SQUALLY WINDS / THUNDERSTORM: Avoid tree climbing and high-boom sprayer operations. Secure young stakes."
                w_influence_kn = "ಬಿರುಗಾಳಿ / ಗುಡುಗು ಮುನ್ನೆಚ್ಚರಿಕೆ: ಮರ ಹತ್ತುವುದು ಮತ್ತು ಎತ್ತರದ ಸಿಂಪಡಣೆ ಕಾರ್ಯಗಳನ್ನು ತಪ್ಪಿಸಿ. ಎಳೆಯ ಸಸಿಗಳಿಗೆ ಆಸರೆ ನೀಡಿ."
                priority = "low"

            activity_record = {
                "farm_id": farm_id,
                "calendar_date": date_str,
                "crop_day": crop_day,
                "monitoring_day": monitoring_day,
                "stage": stage,
                "title_en": tmpl["title_en"],
                "title_kn": tmpl["title_kn"],
                "description_en": tmpl["description_en"],
                "description_kn": tmpl["description_kn"],
                "why_necessary_en": tmpl["why_necessary_en"],
                "why_necessary_kn": tmpl["why_necessary_kn"],
                "timing_conditions_en": tmpl.get("timing_conditions_en"),
                "timing_conditions_kn": tmpl.get("timing_conditions_kn"),
                "priority": priority,
                "weather_influence_en": w_influence_en,
                "weather_influence_kn": w_influence_kn,
                "status": "pending",
                "is_recurring": is_recurring
            }
            selected_activities.append(activity_record)

    # If no activities matched (e.g. gap between cycles), add standard crop inspection
    if not selected_activities:
        selected_activities.append({
            "farm_id": farm_id,
            "calendar_date": date_str,
            "crop_day": crop_day,
            "monitoring_day": monitoring_day,
            "stage": stage,
            "title_en": f"Daily {crop} Field Inspection & Soil Moisture Check",
            "title_kn": f"ದೈನಂದಿನ {crop} ತೋಟ ಪರಿಶೀಲನೆ ಮತ್ತು ತೇವಾಂಶ ತಪಾಸಣೆ",
            "description_en": f"Walk through the {crop} plots. Observe plant vigor, canopy color, weed emergence, and soil surface moisture.",
            "description_kn": f"{crop} ತೋಟದಲ್ಲಿ ಸಂಚರಿಸಿ ಸಸ್ಯಗಳ ಬೆಳವಣಿಗೆ, ಎಲೆಗಳ ಬಣ್ಣ, ಕಳೆ ಮತ್ತು ಮಣ್ಣಿನ ತೇವಾಂಶವನ್ನು ಗಮನಿಸಿ.",
            "why_necessary_en": "Regular daily observation ensures early detection of nutritional deficiencies, moisture deficits, and initial pest infestation.",
            "why_necessary_kn": "ದೈನಂದಿನ ಪರಿಶೀಲನೆಯು ರೋಗ, ಕೀಟ ಮತ್ತು ನೀರಿನ ಕೊರತೆಯನ್ನು ಆರಂಭಿಕ ಹಂತದಲ್ಲೇ ಪತ್ತೆಹಚ್ಚಲು ನೆರವಾಗುತ್ತದೆ.",
            "timing_conditions_en": "Morning between 7:30 AM and 10:00 AM.",
            "timing_conditions_kn": "ಬೆಳಿಗ್ಗೆ 7:30 ರಿಂದ 10:00 ಗಂಟೆಯ ಒಳಗೆ.",
            "priority": "medium",
            "weather_influence_en": "Standard routine field monitoring.",
            "weather_influence_kn": "ದೈನಂದಿನ ಸಾಮಾನ್ಯ ಪರಿಶೀಲನೆ.",
            "status": "pending",
            "is_recurring": True
        })

    # Save to database and return
    saved = save_farm_activities_db(selected_activities)
    return saved

# ==================== Activity Actions ====================

async def mark_activity_done(activity_id: str, farm_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Farmer confirms task completion with timestamp."""
    farm = get_farm_by_id_db(farm_id, user_id)
    if not farm:
        return None
    return update_farm_activity_status_db(activity_id, farm_id, "completed")

async def mark_activity_skipped(
    activity_id: str,
    farm_id: str,
    user_id: str,
    reason: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """Farmer marks task skipped with optional structured reason."""
    farm = get_farm_by_id_db(farm_id, user_id)
    if not farm:
        return None
    return update_farm_activity_status_db(activity_id, farm_id, "skipped", skip_reason=reason)

# ==================== Progress Correction ====================

async def correct_farm_progress(
    farm_id: str,
    user_id: str,
    new_crop_day: Optional[int],
    new_stage: Optional[str],
    reason: Optional[str]
) -> Optional[Dict[str, Any]]:
    """
    Allows farmer to correct farming day or stage if initially misentered.
    Maintains complete audit history in `farm_corrections`.
    """
    farm = get_farm_by_id_db(farm_id, user_id)
    if not farm:
        return None

    timeline = calculate_farm_timeline(farm)
    prev_crop_day = timeline["crop_day"]
    prev_stage = farm["current_stage"]

    corr_data = {
        "farm_id": farm_id,
        "prev_crop_day": prev_crop_day,
        "new_crop_day": new_crop_day,
        "prev_stage": prev_stage,
        "new_stage": new_stage,
        "reason": reason
    }
    create_farm_correction_db(corr_data)

    # Re-fetch updated farm
    updated_farm = get_farm_by_id_db(farm_id, user_id)
    new_tl = calculate_farm_timeline(updated_farm)
    updated_farm["current_crop_day"] = new_tl["crop_day"]
    updated_farm["current_monitoring_day"] = new_tl["monitoring_day"]
    return updated_farm

# ==================== Observations & Harvest ====================

async def add_farm_observation(obs_payload: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
    """Saves daily observation note, soil condition, or pest symptoms."""
    farm_id = obs_payload["farm_id"]
    farm = get_farm_by_id_db(farm_id, user_id)
    if not farm:
        return None

    timeline = calculate_farm_timeline(farm)
    obs_data = {
        **obs_payload,
        "calendar_date": obs_payload.get("calendar_date") or date.today().isoformat(),
        "crop_day": timeline["crop_day"],
        "monitoring_day": timeline["monitoring_day"]
    }
    return create_farm_observation_db(obs_data)

async def add_farm_harvest(harvest_payload: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
    """Records harvest batch connected to this specific farm."""
    farm_id = harvest_payload["farm_id"]
    farm = get_farm_by_id_db(farm_id, user_id)
    if not farm:
        return None
    return create_farm_harvest_db(harvest_payload)
