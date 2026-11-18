"""
Verified Post-Harvest Storage Rules for Dakshina Kannada Crops:
1. Coconut
2. Rice (Paddy)
3. Arecanut
4. Cocoa
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta

STORAGE_METHODS = [
    "Ventilated room",
    "Jute bag",
    "Warehouse",
    "Dark room",
    "Open air",
    "Closed container",
]

CROP_CONDITIONS = [
    "Fresh",
    "Dry",
    "Slightly spoiled",
    "Sprouted",
    "Damp",
    "Overripe",
    "Partially damaged",
]

STORAGE_PROFILES = {
    "Coconut": {
        "name_kn": "ತೆಂಗು",
        "optimal_methods": ["Ventilated room", "Warehouse", "Open air", "Jute bag"],
        "unsuitable_methods": ["Closed container"],
        "acceptable_conditions": ["Fresh", "Dry"],
        "risky_conditions": ["Damp", "Slightly spoiled", "Sprouted", "Partially damaged"],
        "temp_range": "20°C - 28°C",
        "humidity_threshold": "60% - 70% RH",
        "guidelines_en": [
            "Store mature whole coconuts on raised slatted platforms or bamboo racks at least 30 cm above the floor.",
            "Avoid direct contact with moist cement or mud floors to stop mould germination at the eyes.",
            "Ensure cross ventilation to prevent moisture accumulation and premature sprouting.",
            "If storing dried copra, moisture content must be below 6% to prevent Aspergillus flavus aflatoxin and copra beetles."
        ],
        "guidelines_kn": [
            "ಬೆಳೆದ ತೆಂಗಿನಕಾಯಿಗಳನ್ನು ನೆಲದಿಂದ ಕನಿಷ್ಠ 30 ಸೆಂ.ಮೀ ಎತ್ತರದ ಮರದ ಅಥವಾ ಬಿದಿರಿನ ಅಟ್ಟಗಳಲ್ಲಿ ಸಂಗ್ರಹಿಸಿ.",
            "ತೆವಾಂಶವಿರುವ ಸಿಮೆಂಟ್ ಅಥವಾ ಮಣ್ಣಿನ ನೆಲದ ಮೇಲೆ ನೇರವಾಗಿ ಇಡಬೇಡಿ; ಇದು ತೆಂಗಿನಕಣ್ಣುಗಳಲ್ಲಿ ಶಿಲೀಂಧ್ರ ಬೆಳೆಯಲು ಕಾರಣವಾಗುತ್ತದೆ.",
            "ಗಾಳಿಯಾಡುವ ಕೊಠಡಿಯಲ್ಲಿಡಿ; ಗಾಳಿ ಬೆಳಕಿನ ಕೊರತೆಯಿಂದ ಕಾಯಿಗಳು ಅಕಾಲಿಕವಾಗಿ ಮೊಳಕೆಯೊಡೆಯುತ್ತವೆ.",
            "ಕೊಬ್ಬರಿ ಸಂಗ್ರಹಿಸುವಾಗ ತೇವಾಂಶವು ಶೇ. 6 ಕ್ಕಿಂತ ಕಡಿಮೆಯಿರಬೇಕು; ಇಲ್ಲದಿದ್ದರೆ ಕಪ್ಪು ಶಿಲೀಂಧ್ರ ಮತ್ತು ಕೀಟ ಬಾಧೆ ಉಂಟಾಗುತ್ತದೆ."
        ],
        "base_duration_days": {
            "Fresh": 60,
            "Dry": 180,
            "Damp": 15,
            "Slightly spoiled": 7,
            "Sprouted": 5,
            "Partially damaged": 4,
            "Overripe": 20,
        }
    },
    "Rice": {
        "name_kn": "ಭತ್ತ",
        "optimal_methods": ["Jute bag", "Warehouse", "Ventilated room"],
        "unsuitable_methods": ["Open air", "Dark room"],
        "acceptable_conditions": ["Dry"],
        "risky_conditions": ["Damp", "Fresh", "Slightly spoiled", "Sprouted", "Partially damaged"],
        "temp_range": "18°C - 26°C",
        "humidity_threshold": "Below 65% RH, Grain moisture 12-14%",
        "guidelines_en": [
            "Thoroughly sun-dry freshly harvested paddy until grain moisture drops below 13-14% before storage.",
            "Stack jute gunny bags on wooden pallets or dunnage, strictly maintaining 50 cm clearance from walls.",
            "Inspect regularly for rice weevil (*Sitophilus oryzae*) and angoumois grain moth infestation.",
            "Never store damp paddy in sealed airtight bags; anaerobic fermentation causes yellowing and foul odor within 48 hours."
        ],
        "guidelines_kn": [
            "ಕೊಯ್ಲು ಮಾಡಿದ ಭತ್ತವನ್ನು ಸಂಗ್ರಹಿಸುವ ಮುನ್ನ ಧಾನ್ಯದ ತೇವಾಂಶ 12-14% ಕ್ಕಿಂತ ಕಡಿಮೆಯಾಗುವವರೆಗೆ ಬಿಸಿಲಿನಲ್ಲಿ ಚೆನ್ನಾಗಿ ಒಣಗಿಸಿ.",
            "ಗೋಣಿ ಚೀಲಗಳನ್ನು ಮರದ ಹಲಗೆಗಳ (ಪ್ಯಾಲೆಟ್) ಮೇಲೆ ಜೋಡಿಸಿ, ಗೋಡೆಯಿಂದ ಕನಿಷ್ಠ ಅರ್ಧ ಮೀಟರ್ ಅಂತರವನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ.",
            "ಭತ್ತದ ನುಸಿ ಹಾಗೂ ಜೀರುಂಡೆ ಕೀಟಗಳ ಬಾಧೆಯನ್ನು ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ, ಸ್ವಚ್ಛ ಗೋಣಿ ಚೀಲಗಳನ್ನು ಬಳಸಿ.",
            "ತೇವವಿರುವ ಭತ್ತವನ್ನು ಮುಚ್ಚಿದ ಪ್ಲಾಸ್ಟಿಕ್ ಚೀಲಗಳಲ್ಲಿ ಇಡಬೇಡಿ; ತೇವಾಂಶದಿಂದ ಭತ್ತ ಹಳದಿಯಾಗಿ ಕೆಟ್ಟು ದುರ್ವಾಸನೆ ಬೀರುತ್ತದೆ."
        ],
        "base_duration_days": {
            "Dry": 365,
            "Fresh": 14,
            "Damp": 5,
            "Slightly spoiled": 5,
            "Sprouted": 2,
            "Partially damaged": 7,
            "Overripe": 30,
        }
    },
    "Arecanut": {
        "name_kn": "ಅಡಿಕೆ",
        "optimal_methods": ["Jute bag", "Ventilated room", "Warehouse"],
        "unsuitable_methods": ["Closed container", "Open air"],
        "acceptable_conditions": ["Dry"],
        "risky_conditions": ["Damp", "Fresh", "Slightly spoiled", "Partially damaged"],
        "temp_range": "20°C - 30°C",
        "humidity_threshold": "Moisture below 10%, Ambient RH < 65%",
        "guidelines_en": [
            "For Chali supari, ensure whole ripe arecanuts have dried in the sun for 40-45 days until kernel shakes freely inside the husk.",
            "Store in clean, new gunny bags elevated off concrete floors; coastal humidity can cause rapid moisture re-absorption.",
            "Protect storage space from rodents and cigarette beetle (*Lasioderma serricorne*) using clean wire-mesh vents.",
            "If arecanut arrives damp, immediately spread on drying yards under clear sunlight; do not keep bagged."
        ],
        "guidelines_kn": [
            "ಚಾಲಿ ಅಡಿಕೆ ತಯಾರಿಸಲು ಕೊಯ್ಲು ಮಾಡಿದ ಕಾಯಿಗಳನ್ನು 40-45 ದಿನ ಬಿಸಿಲಿನಲ್ಲಿ ಚೆನ್ನಾಗಿ ಒಣಗಿಸಿ, ಕರಕರ ಶಬ್ದ ಬರುವವರೆಗೆ ಒಣಗಿಸಿ ಸುಲಿಯಿರಿ.",
            "ಸಿಮೆಂಟ್ ನೆಲದಿಂದ ತೇವ ಹತ್ತುವುದನ್ನು ತಡೆಯಲು ಹೊಸ ಗೋಣಿ ಚೀಲಗಳಲ್ಲಿ ಮರದ ಹಲಗೆಯ ಮೇಲೆ ಸಂಗ್ರಹಿಸಿ.",
            "ಕರಾವಳಿಯ ತೇವಾಂಶದಿಂದ ಅಡಿಕೆಗೆ ಬೂಷ್ಟು ಬರದಂತೆ ಕಿಟಕಿಗಳಿಗೆ ಜಾಲರಿ ಹಾಕಿ ಕೀಟ ಮತ್ತು ಇಲಿಗಳ ಕಾಟ ತಪ್ಪಿಸಿ.",
            "ಅಡಿಕೆ ತೇವವಾಗಿದ್ದರೆ ಚೀಲದಲ್ಲಿ ಹಾಗೆಯೇ ಇಡಬೇಡಿ, ತಕ್ಷಣ ಬಿಸಿಲಿನಲ್ಲಿ ಹರಡಿ ಒಣಗಿಸಿ."
        ],
        "base_duration_days": {
            "Dry": 365,
            "Fresh": 10,
            "Damp": 6,
            "Slightly spoiled": 7,
            "Sprouted": 3,
            "Partially damaged": 10,
            "Overripe": 20,
        }
    },
    "Cocoa": {
        "name_kn": "ಕೋಕೋ",
        "optimal_methods": ["Jute bag", "Ventilated room", "Warehouse"],
        "unsuitable_methods": ["Closed container", "Dark room", "Open air"],
        "acceptable_conditions": ["Dry"],
        "risky_conditions": ["Damp", "Fresh", "Slightly spoiled", "Overripe", "Partially damaged"],
        "temp_range": "18°C - 25°C",
        "humidity_threshold": "Moisture 7.0% - 8.0%, Ambient RH < 70%",
        "guidelines_en": [
            "Beans must undergo complete fermentation (5-7 days) followed by thorough sun drying to 7.5% moisture.",
            "Store exclusively in food-grade, odor-free jute bags in a dry, odorless warehouse.",
            "Cocoa butter readily absorbs strong external smells; never store near diesel, pesticides, spices, or fertilizer.",
            "Keep stacks away from direct sunlight and ambient damp sea breezes to prevent internal mould."
        ],
        "guidelines_kn": [
            "ಬೀಜಗಳನ್ನು 5-7 ದಿನ ವ್ಯವಸ್ಥಿತವಾಗಿ ಹುದುಗಿಸಿ (ಫರ್ಮೆಂಟೇಶನ್), ನಂತರ ಬಿಸಿಲಿನಲ್ಲಿ ತೇವಾಂಶ 7-8% ಕ್ಕೆ ಇಳಿಯುವವರೆಗೆ ಒಣಗಿಸಿ.",
            "ವಾಸನೆ ಮುಕ್ತ ಶುದ್ಧ ಗೋಣಿ ಚೀಲಗಳಲ್ಲಿ, ಒಣ ಹವೆಯುಳ್ಳ ಉಗ್ರಾಣದಲ್ಲಿ ಮರದ ಹಲಗೆಗಳ ಮೇಲೆ ಸಂಗ್ರಹಿಸಿ.",
            "ಕೋಕೋ ಬೆಣ್ಣೆಯು ವಾತಾವರಣದ ವಾಸನೆಯನ್ನು ತಕ್ಷಣ ಹೀರಿಕೊಳ್ಳುತ್ತದೆ; ಡೀಸೆಲ್, ಕೀಟನಾಶಕ, ಮಸಾಲೆ ಅಥವಾ ರಸಗೊಬ್ಬರಗಳ ಬಳಿ ಇಡಲೇಬೇಡಿ.",
            "ಕರಾವಳಿಯ ಉಪ್ಪು ಗಾಳಿ ಮತ್ತು ತೇವಾಂಶದಿಂದ ಬೀಜದ ಒಳಭಾಗದಲ್ಲಿ ಶಿಲೀಂಧ್ರ ಬರದಂತೆ ಜಾಗ್ರತೆ ವಹಿಸಿ."
        ],
        "base_duration_days": {
            "Dry": 270,
            "Fresh": 4,
            "Damp": 3,
            "Slightly spoiled": 3,
            "Overripe": 7,
            "Partially damaged": 5,
            "Sprouted": 2,
        }
    }
}

def evaluate_storage_practice(
    crop: str,
    harvest_date: str,
    storage_method: str,
    crop_condition: str,
    ambient_temp: float = 28.0,
    ambient_humidity: float = 75.0,
    quantity_kg: float = 0.0,
) -> Dict[str, Any]:
    """
    Evaluates storage conditions based on verified post-harvest science.
    Returns suitability rating, risk indicators, estimated safe shelf life, and selling deadline.
    """
    profile = STORAGE_PROFILES.get(crop, STORAGE_PROFILES["Coconut"])
    
    # Calculate days elapsed since harvest
    try:
        h_date = datetime.strptime(harvest_date, "%Y-%m-%d").date()
    except Exception:
        h_date = datetime.utcnow().date()
    
    today = datetime.utcnow().date()
    days_elapsed = max(0, (today - h_date).days)

    # 1. Evaluate Suitability Rating
    if storage_method in profile["optimal_methods"] and crop_condition in profile["acceptable_conditions"]:
        suitability = "Suitable"
        suitability_kn = "ಅತ್ಯಂತ ಸೂಕ್ತ"
    elif storage_method in profile["unsuitable_methods"] or crop_condition in ["Damp", "Sprouted", "Slightly spoiled"]:
        suitability = "Not Recommended"
        suitability_kn = "ಶಿಫಾರಸು ಮಾಡಲಾಗುವುದಿಲ್ಲ"
    else:
        suitability = "Needs Improvement"
        suitability_kn = "ಸುಧಾರಣೆ ಅಗತ್ಯವಿದೆ"

    # 2. Calculate Safe Duration and Expected Deadline
    base_days = profile["base_duration_days"].get(crop_condition, 30)
    
    # Penalties for suboptimal storage methods or high humidity
    method_factor = 1.0
    if storage_method in profile["unsuitable_methods"]:
        method_factor *= 0.25
    elif storage_method not in profile["optimal_methods"]:
        method_factor *= 0.65

    # Ambient humidity penalty in coastal DK
    if ambient_humidity > 80.0 and crop_condition != "Dry":
        method_factor *= 0.70

    effective_days = int(base_days * method_factor)
    remaining_days = max(1, effective_days - days_elapsed)

    estimated_deadline = today + timedelta(days=remaining_days)

    # 3. Calculate Risk Indicators (Low / Medium / High)
    # Moisture Risk
    if crop_condition in ["Damp", "Fresh"] or ambient_humidity > 82.0:
        moisture_risk = "High"
    elif crop_condition == "Dry" and storage_method in profile["optimal_methods"]:
        moisture_risk = "Low"
    else:
        moisture_risk = "Medium"

    # Spoilage Risk
    if crop_condition in ["Slightly spoiled", "Sprouted", "Damp"] or days_elapsed > effective_days:
        spoilage_risk = "High"
    elif crop_condition == "Fresh" and storage_method in profile["unsuitable_methods"]:
        spoilage_risk = "High"
    elif crop_condition == "Dry":
        spoilage_risk = "Low"
    else:
        spoilage_risk = "Medium"

    # Pest Risk
    if storage_method in ["Open air", "Dark room"]:
        pest_risk = "High"
    elif crop in ["Rice", "Arecanut"] and storage_method == "Warehouse":
        pest_risk = "Medium"
    else:
        pest_risk = "Low"

    # Temperature Risk
    if ambient_temp > 34.0 or ambient_temp < 15.0:
        temp_risk = "High"
    elif ambient_temp > 30.0:
        temp_risk = "Medium"
    else:
        temp_risk = "Low"

    # Explanations
    explanation_en = (
        f"For {crop} in condition '{crop_condition}', using method '{storage_method}' "
        f"provides an estimated safe storage window of ~{remaining_days} remaining days. "
        f"Maintain environmental temperature at {profile['temp_range']} and humidity at {profile['humidity_threshold']}."
    )
    explanation_kn = (
        f"{profile['name_kn']} ಬೆಳೆಯನ್ನು '{crop_condition}' ಸ್ಥಿತಿಯಲ್ಲಿ '{storage_method}' ವಿಧಾನದಲ್ಲಿ ಶೇಖರಿಸಿದರೆ "
        f"ಇನ್ನೂ ಅಂದಾಜು {remaining_days} ದಿನಗಳ ಕಾಲ ಸುರಕ್ಷಿತವಾಗಿ ಇಡಬಹುದು. "
        f"ತಾಪಮಾನ {profile['temp_range']} ಹಾಗೂ ತೇವಾಂಶ {profile['humidity_threshold']} ಮಟ್ಟದಲ್ಲಿ ಇರುವಂತೆ ನಿಗಾ ವಹಿಸಿ."
    )

    return {
        "crop": crop,
        "crop_kn": profile["name_kn"],
        "harvest_date": str(h_date),
        "days_elapsed": days_elapsed,
        "storage_method": storage_method,
        "crop_condition": crop_condition,
        "suitability": suitability,
        "suitability_kn": suitability_kn,
        "temp_range": profile["temp_range"],
        "humidity_threshold": profile["humidity_threshold"],
        "estimated_duration_days": effective_days,
        "remaining_days": remaining_days,
        "estimated_deadline": str(estimated_deadline),
        "risks": {
            "moisture": moisture_risk,
            "spoilage": spoilage_risk,
            "pest": pest_risk,
            "temperature": temp_risk,
        },
        "instructions_en": profile["guidelines_en"],
        "instructions_kn": profile["guidelines_kn"],
        "explanation_en": explanation_en,
        "explanation_kn": explanation_kn,
    }
