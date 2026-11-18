"""
Agricultural Suitability & Plantation Timing Rules for Dakshina Kannada (DK).
Specifically tailored for:
1. Coconut (Cocos nucifera)
2. Rice / Paddy (Oryza sativa)
3. Arecanut (Areca catechu)
4. Cocoa (Theobroma cacao)
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

DK_TALUKS = {
    "Mangaluru": {
        "lat": 12.9141,
        "lon": 74.8560,
        "zone": "Coastal",
        "soil": "Coastal alluvium & Laterite",
        "name_kn": "ಮಂಗಳೂರು",
    },
    "Bantwal": {
        "lat": 12.8946,
        "lon": 75.0345,
        "zone": "Midland / River Valley",
        "soil": "Lateritic clay & Alluvial loam",
        "name_kn": "ಬಂಟ್ವಾಳ",
    },
    "Belthangady": {
        "lat": 12.9965,
        "lon": 75.2570,
        "zone": "Foothills / Western Ghats",
        "soil": "Rich Laterite & Forest Loam",
        "name_kn": "ಬೆಳ್ತಂಗಡಿ",
    },
    "Puttur": {
        "lat": 12.7663,
        "lon": 75.2017,
        "zone": "Midland / Hilly",
        "soil": "Deep Lateritic Loam",
        "name_kn": "ಪುತ್ತೂರು",
    },
    "Sullia": {
        "lat": 12.5606,
        "lon": 75.3905,
        "zone": "Highland / Western Ghats",
        "soil": "Lateritic & Forest Loam",
        "name_kn": "ಸುಳ್ಯ",
    },
    "Moodbidri": {
        "lat": 13.0673,
        "lon": 74.9961,
        "zone": "Midland",
        "soil": "Laterite & Sandy Loam",
        "name_kn": "ಮೂಡುಬಿದಿರೆ",
    },
    "Kadaba": {
        "lat": 12.7628,
        "lon": 75.4026,
        "zone": "Foothills",
        "soil": "Lateritic Clay Loam",
        "name_kn": "ಕಡಬ",
    },
    "Mulki": {
        "lat": 13.0903,
        "lon": 74.7937,
        "zone": "Coastal",
        "soil": "Coastal Sandy Alluvium",
        "name_kn": "ಮುಲ್ಕಿ",
    },
    "Ullal": {
        "lat": 12.8058,
        "lon": 74.8540,
        "zone": "Coastal",
        "soil": "Coastal Sandy Alluvium",
        "name_kn": "ಉಳ್ಳಾಲ",
    },
}

SUPPORTED_CROPS = ["Coconut", "Rice", "Arecanut", "Cocoa"]

CROP_PROFILES = {
    "Coconut": {
        "name": "Coconut",
        "scientific_name": "Cocos nucifera",
        "name_kn": "ತೆಂಗು",
        "image": "https://images.unsplash.com/photo-1544943910-4c1dc44a0b4d?auto=format&fit=crop&w=800&q=80",
        "optimal_temp_range": (20.0, 34.0),
        "ideal_temp": 27.0,
        "water_requirement": ["Moderate", "High"],
        "min_annual_rainfall_mm": 1300,
        "soil_types": ["Coastal alluvium", "Laterite", "Red sandy loam"],
        "planting_seasons": [
            {
                "season": "Pre-Monsoon / Monsoon Onset",
                "months": [5, 6],
                "description_en": "May to June: Ideal with the commencement of the South-West monsoon in DK.",
                "description_kn": "ಮೇ - ಜೂನ್: ದಕ್ಷಿಣ ಕನ್ನಡದಲ್ಲಿ ನೈಋತ್ಯ ಮಾನ್ಸೂನ್ ಆರಂಭದೊಂದಿಗೆ ತೆಂಗಿನ ಸಸಿ ನೆಡಲು ಅತ್ಯಂತ ಸೂಕ್ತ.",
            },
            {
                "season": "Post-Monsoon",
                "months": [9, 10],
                "description_en": "September to October: Best for heavy low-lying areas after heavy flood-water drains.",
                "description_kn": "ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್: ಭಾರಿ ಮಳೆ ನಿಂತ ನಂತರ ತಗ್ಗು ಪ್ರದೇಶಗಳಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಸಸಿ ನೆಡಲು ಸೂಕ್ತ.",
            }
        ],
        "precautions_en": [
            "Dig planting pits of 1m x 1m x 1m at least 2 months prior and expose to sunlight.",
            "Fill bottom 50-60cm with topsoil, organic manure, and 50g neem cake to prevent termite attack.",
            "Ensure effective drainage channels; waterlogging during July monsoon peaks triggers bud rot.",
            "Maintain optimal spacing of 7.5m x 7.5m (triangular or square system)."
        ],
        "precautions_kn": [
            "ಕನಿಷ್ಠ 2 ತಿಂಗಳು ಮುಂಚಿತವಾಗಿ 1x1x1 ಮೀಟರ್ ಗಾತ್ರದ ಗುಂಡಿ ತೋಡಿ ಬಿಸಿಲಿನಲ್ಲಿ ಒಣಗಲು ಬಿಡಿ.",
            "ಗುಂಡಿಯ ತಳಭಾಗಕ್ಕೆ ಮೇಲ್ಮಣ್ಣು, ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಮತ್ತು ಗೆದ್ದಲು ನಿಯಂತ್ರಣಕ್ಕೆ 50 ಗ್ರಾಂ ಬೇವಿನ ಹಿಂಡಿ ಬೆರೆಸಿ.",
            "ನೀರು ನಿಲ್ಲದಂತೆ ಉತ್ತಮ ಚರಂಡಿ ವ್ಯವಸ್ಥೆ ಮಾಡಿ; ಜುಲೈ ಮಳೆಯಲ್ಲಿ ನೀರು ನಿಂತರೆ ಸುಳಿ ಕೊಳೆ ರೋಗ ಬರುವ ಸಾಧ್ಯತೆಯಿದೆ.",
            "ಗಿಡಗಳ ನಡುವೆ ಕನಿಷ್ಠ 7.5 x 7.5 ಮೀಟರ್ ಅಂತರವನ್ನು ಕಡ್ಡಾಯವಾಗಿ ಕಾಪಾಡಿಕೊಳ್ಳಿ."
        ]
    },
    "Rice": {
        "name": "Rice",
        "scientific_name": "Oryza sativa (Paddy)",
        "name_kn": "ಭತ್ತ",
        "image": "https://images.unsplash.com/photo-1536304993881-ff6e9eefa2a6?auto=format&fit=crop&w=800&q=80",
        "optimal_temp_range": (20.0, 36.0),
        "ideal_temp": 28.0,
        "water_requirement": ["High"],
        "min_annual_rainfall_mm": 2000,
        "soil_types": ["Clay loam", "Coastal valley alluvium", "Silty clay"],
        "planting_seasons": [
            {
                "season": "Enne / Karthika (Kharif)",
                "months": [5, 6, 7],
                "description_en": "Late May (nursery) to June-July (transplanting): Main rainfed paddy crop in DK.",
                "description_kn": "ಮೇ ಕೊನೆಗೆ ನರ್ಸರಿ ತಯಾರಿಕೆ, ಜೂನ್-ಜುಲೈನಲ್ಲಿ ನಾಟಿ: ಕರಾವಳಿಯ ಮುಖ್ಯ ಮುಂಗಾರು ಬೆಳೆ.",
            },
            {
                "season": "Suggi (Rabi)",
                "months": [10, 11],
                "description_en": "October to November: Suitable for wetland areas with residual moisture and valley springs.",
                "description_kn": "ಅಕ್ಟೋಬರ್ - ನವೆಂಬರ್: ಹಿಂಗಾರು ಮಳೆ ಮತ್ತು ಕಣಿವೆ ಪ್ರದೇಶದ ನೀರಿನ ಲಭ್ಯತೆಯೊಂದಿಗೆ ಎರಡನೇ ಬೆಳೆ.",
            }
        ],
        "precautions_en": [
            "Prepare nursery beds 25 days before expected monsoon transplanting.",
            "Incorporate green manure (dhaincha / sunhemp) during summer puddling.",
            "Maintain 2-5 cm standing water during tillering stage; drain field before panicle initiation.",
            "Strengthen field bunds before heavy coastal rains to prevent soil erosion."
        ],
        "precautions_kn": [
            "ನಾಟಿ ಮಾಡುವ 25 ದಿನಗಳ ಮೊದಲು ವ್ಯವಸ್ಥಿತ ನರ್ಸರಿ ಮಡಿಗಳನ್ನು ಸಿದ್ಧಪಡಿಸಿ.",
            "ಬೇಸಿಗೆಯಲ್ಲಿ ಹೊಲ ಉಳುಮೆ ಮಾಡುವಾಗ ಹಸಿರೆಲೆ ಗೊಬ್ಬರ ಅಥವಾ ಸೆಣಬನ್ನು ಮಣ್ಣಿನಲ್ಲಿ ಬೆರೆಸಿ.",
            "ತೆನೆ ಕಟ್ಟುವ ಹಂತದಲ್ಲಿ 2-5 ಸೆಂ.ಮೀ ನೀರನ್ನು ನಿಲ್ಲಿಸಿ, ನಂತರ ನಿಯಂತ್ರಿತ ಬಸಿಗಾಲುವೆ ನಿರ್ವಹಿಸಿ.",
            "ಕರಾವಳಿಯ ಭಾರಿ ಮಳೆಯಿಂದ ಮಣ್ಣು ಕೊಚ್ಚಿ ಹೋಗದಂತೆ ಗದ್ದೆ ಬದುಗಳನ್ನು ಭದ್ರಪಡಿಸಿ."
        ]
    },
    "Arecanut": {
        "name": "Arecanut",
        "scientific_name": "Areca catechu (Betel Nut)",
        "name_kn": "ಅಡಿಕೆ",
        "image": "https://images.unsplash.com/photo-1629813366051-b58137b2792c?auto=format&fit=crop&w=800&q=80",
        "optimal_temp_range": (15.0, 35.0),
        "ideal_temp": 26.0,
        "water_requirement": ["Moderate", "High"],
        "min_annual_rainfall_mm": 1800,
        "soil_types": ["Deep laterite", "Red clay loam", "Valley soils"],
        "planting_seasons": [
            {
                "season": "South-West Monsoon Onset",
                "months": [5, 6],
                "description_en": "May to June: With early monsoon showers, ensures fast root establishment.",
                "description_kn": "ಮೇ - ಜೂನ್: ಮುಂಗಾರು ಮಳೆಯ ಮೊದಲ ದಿನಗಳಲ್ಲಿ ಸಸಿ ನಾಟಿ ಮಾಡುವುದರಿಂದ ಬೇರುಗಳು ಗಟ್ಟಿಯಾಗಿ ಹಿಡಿಯುತ್ತವೆ.",
            },
            {
                "season": "Post-Monsoon Window",
                "months": [9, 10],
                "description_en": "September to October: Highly recommended in areas with severe waterlogging during peak monsoon.",
                "description_kn": "ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್: ಜುಲೈ-ಆಗಸ್ಟ್‌ನಲ್ಲಿ ಅತಿಯಾದ ನೀರು ನಿಲ್ಲುವ ತೋಟಗಳಲ್ಲಿ ಹಿಂಗಾರು ಆರಂಭದಲ್ಲಿ ನಾಟಿ ಮಾಡುವುದು ಉತ್ತಮ.",
            }
        ],
        "precautions_en": [
            "Pits of 90cm x 90cm x 90cm spaced 2.7m x 2.7m apart.",
            "Provide shade for young seedlings using banana plants to shield from harsh south-western afternoon sun.",
            "Apply prophylactic 1% Bordeaux mixture on bunches before monsoon onset to prevent Mahali/Koleroga.",
            "Establish drainage trenches at every two rows in laterite slopes."
        ],
        "precautions_kn": [
            "90x90x90 ಸೆಂ.ಮೀ ಗುಂಡಿಗಳನ್ನು 2.7 x 2.7 ಮೀಟರ್ ಅಂತರದಲ್ಲಿ ನಿರ್ಮಿಸಿ.",
            "ಎಳೆಯ ಸಸಿಗಳಿಗೆ ಮಧ್ಯಾಹ್ನದ ಕಠಿಣ ಬಿಸಿಲು ತಾಗದಂತೆ ನೆರಳಿಗಾಗಿ ಬಾಳೆ ಗಿಡಗಳನ್ನು ಅಂತರಬೆಳೆಯಾಗಿ ನೆಡಿ.",
            "ಮುಂಗಾರು ಮಳೆ ಆರಂಭಕ್ಕೂ ಮುನ್ನ ಕೊಳೆರೋಗ (ಮಹಾಲಿ) ತಡೆಗಟ್ಟಲು ಶೇ. 1ರ ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ.",
            "ಇಳಿಜಾರು ಜಾಗದಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ಪ್ರತಿ ಎರಡು ಸಾಲುಗಳಿಗೆ ಒಂದರಂತೆ ಬಸಿಗಾಲುವೆ ತೋಡಿ."
        ]
    },
    "Cocoa": {
        "name": "Cocoa",
        "scientific_name": "Theobroma cacao",
        "name_kn": "ಕೋಕೋ",
        "image": "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?auto=format&fit=crop&w=800&q=80",
        "optimal_temp_range": (18.0, 34.0),
        "ideal_temp": 25.0,
        "water_requirement": ["Moderate"],
        "min_annual_rainfall_mm": 1500,
        "soil_types": ["Organic rich laterite", "Alluvial loam", "Under-canopy garden soil"],
        "planting_seasons": [
            {
                "season": "Monsoon Intercrop Window",
                "months": [6, 7],
                "description_en": "June to July: Planted as a companion/intercrop in Arecanut and Coconut gardens.",
                "description_kn": "ಜೂನ್ - ಜುಲೈ: ಅಡಿಕೆ ಮತ್ತು ತೆಂಗಿನ ತೋಟಗಳಲ್ಲಿ ಅಂತರಬೆಳೆಯಾಗಿ ನೆಡಲು ಮಳೆಗಾಲದ ತಿಂಗಳುಗಳು ಪ್ರಶಸ್ತ.",
            }
        ],
        "precautions_en": [
            "Must be planted under 40-50% shade; ideal as an intercrop in mature arecanut or coconut palms.",
            "Pits of 50cm x 50cm x 50cm placed in the center of 4 arecanut palms.",
            "Prune early shoots to maintain a single upright stem up to 1.5m before allowing jorquette branch canopy.",
            "Protect young cocoa seedlings from waterlogging and black pod disease (*Phytophthora palmivora*)."
        ],
        "precautions_kn": [
            "40-50% ನೆರಳಿನ ಅಗತ್ಯವಿದೆ; ಬೆಳೆದ ಅಡಿಕೆ ಅಥವಾ ತೆಂಗಿನ ಮರಗಳ ನಡುವೆ ಅಂತರಬೆಳೆಯಾಗಿ ಬೆಳೆಸುವುದು ಸೂಕ್ತ.",
            "ನಾಲ್ಕು ಅಡಿಕೆ ಮರಗಳ ಮಧ್ಯದಲ್ಲಿ 50x50x50 ಸೆಂ.ಮೀ ಗುಂಡಿಗಳನ್ನು ತೆಗೆಯಿರಿ.",
            "1.5 ಮೀಟರ್ ಎತ್ತರದವರೆಗೆ ಒಂದೇ ಮುಖ್ಯ ಕಾಂಡ ಬೆಳೆಯುವಂತೆ ಪಕ್ಕದ ಕವಲುಗಳನ್ನು ಕತ್ತರಿಸಿ (ಪ್ರೂನಿಂಗ್).",
            "ಕಪ್ಪು ಕಾಯಿ ರೋಗ ಬರದಂತೆ ಮತ್ತು ಬೇರಿನ ಬಳಿ ನೀರು ನಿಲ್ಲದಂತೆ ಎಚ್ಚರವಹಿಸಿ."
        ]
    }
}

def evaluate_crop_suitability(
    taluk: str,
    water_availability: str,
    current_temp: float,
    current_humidity: float,
    rainfall_forecast_mm: float,
    current_month: int,
    soil_type: Optional[str] = None,
    irrigation_available: Optional[bool] = None,
) -> Dict[str, Any]:
    """
    Evaluates suitability for all 4 supported crops based on DK agricultural rules.
    Returns ranked recommendations with scientifically justified suitability scores.
    """
    taluk_info = DK_TALUKS.get(taluk, DK_TALUKS["Mangaluru"])
    results = []

    for crop_name, profile in CROP_PROFILES.items():
        score = 0
        reasons_en = []
        reasons_kn = []
        warnings_en = []
        warnings_kn = []

        # 1. Water Availability check (Weight: 35)
        water_req = profile["water_requirement"]
        if water_availability in water_req:
            score += 35
            reasons_en.append(f"Water availability '{water_availability}' matches requirement for {crop_name}.")
            reasons_kn.append(f"ಲಭ್ಯವಿರುವ ನೀರಿನ ಪ್ರಮಾಣ '{water_availability}' {profile['name_kn']} ಬೆಳೆಗೆ ಸಮರ್ಪಕವಾಗಿದೆ.")
        elif water_availability == "Low" and "Moderate" in water_req:
            score += 15
            warnings_en.append(f"{crop_name} will require supplemental drip or sprinkler irrigation during dry months.")
            warnings_kn.append(f"ಒಣ ಹವೆಯ ತಿಂಗಳುಗಳಲ್ಲಿ {profile['name_kn']} ಬೆಳೆಗೆ ಹನಿ ನೀರಾವರಿ ಅಗತ್ಯವಿದೆ.")
        elif water_availability == "High" and "Moderate" in water_req:
            score += 25
            warnings_en.append(f"Ensure deep trenches; excess standing water in high rainfall zones can cause root issues.")
            warnings_kn.append(f"ಹೆಚ್ಚು ನೀರು ನಿಲ್ಲದಂತೆ ಬಸಿಗಾಲುವೆಗಳ ನಿರ್ವಹಣೆ ಅಗತ್ಯ.")
        else:
            score += 10
            warnings_en.append(f"Water availability '{water_availability}' is below optimal for {crop_name}.")
            warnings_kn.append(f"ಲಭ್ಯವಿರುವ ನೀರು {profile['name_kn']} ಬೆಳೆಯ ಅಗತ್ಯಕ್ಕಿಂತ ಕಡಿಮೆ ಇದೆ.")

        # 2. Temperature and Humidity Compatibility (Weight: 25)
        min_temp, max_temp = profile["optimal_temp_range"]
        if min_temp <= current_temp <= max_temp:
            score += 25
            reasons_en.append(f"Current temperature ({current_temp:.1f}°C) is within optimal range ({min_temp}-{max_temp}°C).")
            reasons_kn.append(f"ಪ್ರಸ್ತುತ ತಾಪಮಾನ ({current_temp:.1f}°C) ಸೂಕ್ತ ವ್ಯಾಪ್ತಿಯಲ್ಲಿದೆ ({min_temp}-{max_temp}°C).")
        else:
            score += 10
            warnings_en.append(f"Temperature {current_temp:.1f}°C is outside optimal range ({min_temp}-{max_temp}°C).")
            warnings_kn.append(f"ತಾಪಮಾನ {current_temp:.1f}°C ಸೂಕ್ತ ಮಟ್ಟಕ್ಕಿಂತ ವ್ಯತ್ಯಾಸವಾಗಿದೆ.")

        # 3. Seasonal Planting Window Timing (Weight: 25)
        matched_season = None
        for s in profile["planting_seasons"]:
            if current_month in s["months"]:
                matched_season = s
                break

        if matched_season:
            score += 25
            plantation_window_en = f"Optimal Plantation Window: {matched_season['season']} ({matched_season['description_en']})"
            plantation_window_kn = f"ಸೂಕ್ತ ನಾಟಿ ಸಮಯ: {matched_season['season']} ({matched_season['description_kn']})"
            reasons_en.append(f"Current calendar period coincides with {matched_season['season']}.")
            reasons_kn.append(f"ಪ್ರಸ್ತುತ ಸಮಯವು {matched_season['season']} ನಾಟಿ ಅವಧಿಗೆ ಸರಿಹೊಂದುತ್ತದೆ.")
        else:
            # Look up next upcoming season
            next_season = profile["planting_seasons"][0]
            plantation_window_en = f"Upcoming Window: {next_season['season']} (Prepare land & nursery now)"
            plantation_window_kn = f"ಮುಂಬರುವ ನಾಟಿ ಸಮಯ: {next_season['season']} (ಈಗಿನಿಂದಲೇ ಭೂಮಿ ಹಾಗೂ ಸಸಿ ತಯಾರಿ ಆರಂಭಿಸಿ)"
            score += 12
            reasons_en.append(f"Current period is pre-season; recommended for pit excavation, soil solarization, and nursery.")
            reasons_kn.append(f"ಇದು ನಾಟಿ ಪೂರ್ವ ಸಿದ್ಧತೆಯ ಸಮಯ; ಗುಂಡಿ ತೋಡುವುದು ಹಾಗೂ ಗೊಬ್ಬರ ಸಂಗ್ರಹಕ್ಕೆ ಪ್ರಶಸ್ತ.")

        # 4. Taluk Agro-ecological fit (Weight: 15)
        if taluk_info["zone"] == "Coastal":
            if crop_name in ["Coconut", "Rice"]:
                score += 15
                reasons_en.append(f"Highly adapted to coastal DK soil and marine humidity ({taluk}).")
                reasons_kn.append(f"ಕರಾವಳಿ ವಲಯದ ({taluk_info['name_kn']}) ಮರಳು ಮಿಶ್ರಿತ ಗೋಡು ಮಣ್ಣಿಗೆ ಹೆಚ್ಚು ಹೊಂದಿಕೊಳ್ಳುತ್ತದೆ.")
            else:
                score += 10
        elif taluk_info["zone"] in ["Midland / River Valley", "Foothills / Western Ghats", "Highland / Western Ghats", "Foothills"]:
            if crop_name in ["Arecanut", "Cocoa", "Coconut"]:
                score += 15
                reasons_en.append(f"Well suited to interior DK laterite slopes and fertile valley floors ({taluk}).")
                reasons_kn.append(f"ಒಳನಾಡಿನ ಲ್ಯಾಟರೈಟ್ ಮಣ್ಣು ಮತ್ತು ಕಣಿವೆ ತೋಟಗಳಿಗೆ ({taluk_info['name_kn']}) ಅತಿ ಸೂಕ್ತ.")
            else:
                score += 12

        # Cap score at 100
        score = min(100, max(20, score))

        results.append({
            "crop": crop_name,
            "crop_kn": profile["name_kn"],
            "scientific_name": profile["scientific_name"],
            "image": profile["image"],
            "suitability_score": score,
            "water_suitability": water_availability,
            "plantation_window_en": plantation_window_en,
            "plantation_window_kn": plantation_window_kn,
            "reasons_en": reasons_en,
            "reasons_kn": reasons_kn,
            "precautions_en": profile["precautions_en"],
            "precautions_kn": profile["precautions_kn"],
            "warnings_en": warnings_en,
            "warnings_kn": warnings_kn,
            "taluk": taluk,
            "taluk_kn": taluk_info["name_kn"],
            "taluk_zone": taluk_info["zone"],
        })

    # Sort descending by suitability score
    results.sort(key=lambda x: x["suitability_score"], reverse=True)

    return {
        "taluk": taluk,
        "taluk_kn": taluk_info["name_kn"],
        "taluk_zone": taluk_info["zone"],
        "soil_profile": taluk_info["soil"],
        "evaluated_at": datetime.utcnow().isoformat(),
        "primary_recommendation": results[0],
        "all_recommendations": results,
    }
