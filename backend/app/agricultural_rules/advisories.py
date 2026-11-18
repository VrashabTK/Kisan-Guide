"""
Agricultural Weather-Based Farming Routines & Precautions for Dakshina Kannada.
Generates crop-specific daily and 3-4 day farming advisories grounded in agronomic science.
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta

def generate_farming_advisories(
    weather_summary: Dict[str, Any],
    selected_crop: str = "All",
    forecast_days: List[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Generates actionable, crop-specific farming routines based on forecasted weather.
    """
    advisories = []
    
    current_temp = weather_summary.get("temperature", 28.0)
    current_humidity = weather_summary.get("humidity", 78.0)
    current_rain = weather_summary.get("rainfall", 0.0)
    precipitation_prob = weather_summary.get("precipitation_probability", 20.0)
    wind_speed = weather_summary.get("wind_speed", 10.0)
    weather_code = weather_summary.get("weather_code", 0)

    is_rainy = current_rain > 5.0 or precipitation_prob > 60.0 or weather_code in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]
    is_heavy_rain = current_rain > 30.0 or weather_code in [65, 82, 95, 96, 99]
    is_hot_dry = current_temp > 33.0 and current_rain < 1.0

    today = datetime.utcnow().strftime("%Y-%m-%d")
    tomorrow = (datetime.utcnow() + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (datetime.utcnow() + timedelta(days=2)).strftime("%Y-%m-%d")

    # 1. Heavy Rain / Thunderstorm Advisories
    if is_heavy_rain:
        advisories.append({
            "id": "adv_drainage_01",
            "date": today,
            "category": "Field Drainage",
            "category_kn": "ಬಸಿಗಾಲುವೆ ನಿರ್ವಹಣೆ",
            "importance": "Critical",
            "crop": "Arecanut, Coconut, Cocoa",
            "crop_kn": "ಅಡಿಕೆ, ತೆಂಗು, ಕೋಕೋ",
            "title_en": "Clear Drainage Trenches for Root Protection",
            "title_kn": "ಬೇರುಗಳ ರಕ್ಷಣೆಗೆ ತೋಟದ ಬಸಿಗಾಲುವೆಗಳನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ",
            "task_en": "Inspect and open all sub-drains and main field canals to prevent waterlogging around palm roots.",
            "task_kn": "ಅಡಿಕೆ ಮತ್ತು ತೆಂಗಿನ ಮರಗಳ ಬೇರಿನ ಬಳಿ ನೀರು ನಿಲ್ಲದಂತೆ ಎಲ್ಲಾ ಬಸಿಗಾಲುವೆಗಳ ಹೂಳೆತ್ತಿ ಸರಾಗವಾಗಿ ನೀರು ಹರಿದುಹೋಗಲು ವ್ಯವಸ್ಥೆ ಮಾಡಿ.",
            "reason_en": f"Forecast indicates heavy precipitation ({current_rain:.1f} mm). Stagnant water triggers root asphyxiation and Mahali/bud rot disease.",
            "reason_kn": f"ಭಾರಿ ಮಳೆಯ ಮುನ್ಸೂಚನೆ ({current_rain:.1f} ಮಿ.ಮೀ) ಇರುವುದರಿಂದ ನೀರು ನಿಂತರೆ ಬೇರು ಕೊಳೆ ಹಾಗೂ ಸುಳಿ ಕೊಳೆ ರೋಗದ ಅಪಾಯ ಹೆಚ್ಚುತ್ತದೆ."
        })
        advisories.append({
            "id": "adv_fertilizer_01",
            "date": today,
            "category": "Fertilizer Precautions",
            "category_kn": "ಗೊಬ್ಬರ ನಿರ್ವಹಣೆ",
            "importance": "High",
            "crop": "All Crops",
            "crop_kn": "ಎಲ್ಲಾ ಬೆಳೆಗಳು",
            "title_en": "Postpone Chemical Fertilizer & Spraying Operations",
            "title_kn": "ರಾಸಾಯನಿಕ ಗೊಬ್ಬರ ಹಾಗೂ ಔಷಧ ಸಿಂಪಡಣೆಯನ್ನು ಮುಂದೂಡಿ",
            "task_en": "Do not apply chemical urea, potassic fertilizers, or foliar pesticides during active downpours.",
            "task_kn": "ಭಾರಿ ಮಳೆಯ ಸಮಯದಲ್ಲಿ ಯೂರಿಯಾ, ಪೊಟ್ಯಾಷ್ ಗೊಬ್ಬರ ಅಥವಾ ಕೀಟನಾಶಕ ಸಿಂಪಡಣೆ ಮಾಡಬೇಡಿ.",
            "reason_en": "Heavy runoff will wash away applied nutrients into waterways, resulting in complete chemical loss.",
            "reason_kn": "ಮಳೆಯ ನೀರಿನಲ್ಲಿ ರಸಗೊಬ್ಬರ ಕೊಚ್ಚಿಹೋಗಿ ಸಂಪೂರ್ಣ ನಷ್ಟವಾಗುತ್ತದೆ."
        })
        advisories.append({
            "id": "adv_paddy_bund_01",
            "date": tomorrow,
            "category": "Field Management",
            "category_kn": "ಗದ್ದೆ ಬದು ನಿರ್ವಹಣೆ",
            "importance": "High",
            "crop": "Rice",
            "crop_kn": "ಭತ್ತ",
            "title_en": "Regulate Paddy Field Weir Outlets",
            "title_kn": "ಭತ್ತದ ಗದ್ದೆಗಳ ತೂಬು ಹಾಗೂ ಬದುಗಳನ್ನು ತೆರೆಯಿರಿ",
            "task_en": "Create controlled spillways on field bunds to discharge excess monsoon surge while keeping 3-5 cm optimum water level.",
            "task_kn": "ಗದ್ದೆಯಲ್ಲಿ ಅತಿಯಾದ ನೀರು ನಿಲ್ಲದಂತೆ ತೂಬುಗಳನ್ನು ತೆರೆದು ಕೇವಲ 3-5 ಸೆಂ.ಮೀ ನೀರು ಉಳಿಯುವಂತೆ ಹೆಚ್ಚುವರಿ ನೀರನ್ನು ಹೊರಬಿಡಿ.",
            "reason_en": "Submergence of young rice seedlings for more than 48 hours retards tillering.",
            "reason_kn": "ಎಳೆಯ ಭತ್ತದ ಸಸಿಗಳು 48 ಗಂಟೆಗಳಿಗೂ ಹೆಚ್ಚು ಕಾಲ ನೀರಿನಲ್ಲಿ ಮುಳುಗಿದ್ದರೆ ಸಸಿ ಕೊಳೆತು ಹಾಳಾಗುತ್ತದೆ."
        })

    # 2. Moderate Rain / Humid Weather
    elif is_rainy:
        advisories.append({
            "id": "adv_crop_prot_01",
            "date": today,
            "category": "Crop Protection",
            "category_kn": "ಬೆಳೆ ಸಂರಕ್ಷಣೆ",
            "importance": "High",
            "crop": "Arecanut",
            "crop_kn": "ಅಡಿಕೆ",
            "title_en": "Bordeaux Mixture Application Window",
            "title_kn": "ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಣೆ",
            "task_en": "Prepare 1% Bordeaux mixture with rosin soap sticker for spraying arecanut bunches during rain breaks.",
            "task_kn": "ಮಳೆ ಬಿಡುವು ನೀಡಿದಾಗ ಅಡಿಕೆ ಗೊನೆಗಳಿಗೆ ಶೇ. 1 ರ ಬೋರ್ಡೋ ದ್ರಾವಣಕ್ಕೆ ಅಂಟು ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ.",
            "reason_en": f"High humidity ({current_humidity:.0f}%) fosters Phytophthora meadii (Fruit rot / Mahali) spores on tender arecanut bunches.",
            "reason_kn": f"ಗಾಳಿಯಲ್ಲಿನ ಅತಿಯಾದ ತೇವಾಂಶವು ({current_humidity:.0f}%) ಕೊಳೆರೋಗದ ಶಿಲೀಂಧ್ರ ಹರಡಲು ಕಾರಣವಾಗುತ್ತದೆ."
        })
        advisories.append({
            "id": "adv_cocoa_prune_01",
            "date": tomorrow,
            "category": "Crop Care",
            "category_kn": "ಗಿಡ ನಿರ್ವಹಣೆ",
            "importance": "Medium",
            "crop": "Cocoa",
            "crop_kn": "ಕೋಕೋ",
            "title_en": "Cocoa Canopy Sanitation & Pruning",
            "title_kn": "ಕೋಕೋ ಗಿಡಗಳ ರೆಂಬೆ ಕತ್ತರಿಸುವುದು ಮತ್ತು ಸ್ವಚ್ಛತೆ",
            "task_en": "Remove infected, black pods from cocoa trees and prune excessive chupons to improve air circulation.",
            "task_kn": "ಕಪ್ಪು ಕಾಯಿ ರೋಗ ಪೀಡಿತ ಕೋಕೋ ಕಾಯಿಗಳನ್ನು ಕಿತ್ತು ನಾಶಪಡಿಸಿ, ಗಾಳಿಯಾಡಲು ಅನಗತ್ಯ ರೆಂಬೆಗಳನ್ನು ಕತ್ತರಿಸಿ.",
            "reason_en": "Dense canopy traps micro-humidity, triggering Phytophthora pod rot.",
            "reason_kn": "ಹೆಚ್ಚು ಕವಲುಗಳಿದ್ದರೆ ತೇವಾಂಶ ನಿಂತು ಕಾಯಿ ಕೊಳೆ ರೋಗ ಹೆಚ್ಚುತ್ತದೆ."
        })

    # 3. Hot / Dry Weather (Summer / Post-monsoon break)
    elif is_hot_dry:
        advisories.append({
            "id": "adv_irrigation_01",
            "date": today,
            "category": "Irrigation",
            "category_kn": "ನೀರಾವರಿ",
            "importance": "Critical",
            "crop": "Arecanut, Coconut",
            "crop_kn": "ಅಡಿಕೆ, ತೆಂಗು",
            "title_en": "Schedule Evening Drip / Basin Irrigation",
            "title_kn": "ಸಂಜೆ ವೇಳೆ ಹನಿ ನೀರಾವರಿ ಅಥವಾ ಪಾತಿ ನೀರುಣಿಸಿ",
            "task_en": "Deliver 150-200 liters of water per adult coconut palm and 20-30 liters per areca palm every 3-4 days.",
            "task_kn": "ಪ್ರತಿ ತೆಂಗಿನ ಮರಕ್ಕೆ 150-200 ಲೀಟರ್ ಹಾಗೂ ಅಡಿಕೆ ಮರಕ್ಕೆ 20-30 ಲೀಟರ್ ನೀರನ್ನು ಸಂಜೆ ವೇಳೆ ಹಾಯಿಸಿ.",
            "reason_en": f"Ambient temperature ({current_temp:.1f}°C) causes high evapotranspiration in sandy and laterite soils.",
            "reason_kn": f"ಹೆಚ್ಚಿನ ತಾಪಮಾನದಿಂದ ({current_temp:.1f}°C) ಮಣ್ಣಿನಲ್ಲಿನ ತೇವಾಂಶ ಬೇಗನೆ ಆವಿಯಾಗುತ್ತದೆ."
        })
        advisories.append({
            "id": "adv_mulching_01",
            "date": tomorrow,
            "category": "Soil Moisture Conservation",
            "category_kn": "ಮಣ್ಣಿನ ತೇವಾಂಶ ಸಂರಕ್ಷಣೆ",
            "importance": "High",
            "crop": "Coconut, Cocoa, Arecanut",
            "crop_kn": "ತೆಂಗು, ಕೋಕೋ, ಅಡಿಕೆ",
            "title_en": "Mulch Palm Basins with Organic Waste",
            "title_kn": "ಮರದ ಬುಡಕ್ಕೆ ತೆಂಗಿನ ಗರಿ ಅಥವಾ ಒಣ ತ್ಯಾಜ್ಯದಿಂದ ಹೊದಿಕೆ (ಮಲ್ಚಿಂಗ್) ಹಾಕಿ",
            "task_en": "Spread dry arecanut leaves, coconut fronds, or dried grass in a 2-meter radius basin around trunks.",
            "task_kn": "ಮರಗಳ ಬುಡದಿಂದ 2 ಮೀಟರ್ ವ್ಯಾಪ್ತಿಯಲ್ಲಿ ಒಣ ಎಲೆ, ಕಳೆ ಅಥವಾ ತೆಂಗಿನ ಸಿಪ್ಪೆಗಳನ್ನು ಹರಡಿ.",
            "reason_en": "Mulching moderates root zone temperature, retards weed growth, and saves up to 40% irrigation water.",
            "reason_kn": "ಹೊದಿಕೆ ಹಾಕುವುದರಿಂದ ಬೇರುಗಳು ತಂಪಾಗಿರುತ್ತವೆ ಹಾಗೂ ಶೇ. 40 ರಷ್ಟು ನೀರಿನ ಉಳಿತಾಯವಾಗುತ್ತದೆ."
        })
        advisories.append({
            "id": "adv_sunscorch_01",
            "date": day_after,
            "category": "Plant Protection",
            "category_kn": "ಬಿಸಿಲಿನಿಂದ ರಕ್ಷಣೆ",
            "importance": "Medium",
            "crop": "Arecanut",
            "crop_kn": "ಅಡಿಕೆ",
            "title_en": "White-wash Arecanut Trunks Against Sun-Scorch",
            "title_kn": "ಅಡಿಕೆ ಮರದ ಕಾಂಡಗಳಿಗೆ ಸುಣ್ಣ ಬಳಿಯಿರಿ",
            "task_en": "Paint south-western exposed palm trunks with 20% slaked lime wash or tie arecanut fronds.",
            "task_kn": "ದಕ್ಷಿಣ-ಪಶ್ಚಿಮ ದಿಕ್ಕಿನಿಂದ ಬೀಳುವ ಕಡು ಬಿಸಿಲಿನಿಂದ ಕಾಂಡ ಬಿರಿಯದಂತೆ ಮರಕ್ಕೆ ಸುಣ್ಣ ಬಳಿಯಿರಿ.",
            "reason_en": "Severe solar radiation causes trunk burst and bark cracking on exposed border palms.",
            "reason_kn": "ತೀವ್ರ ಬಿಸಿಲಿನಿಂದ ಗಿಡದ ಕಾಂಡ ಸೀಳಿ ಹಾನಿಯಾಗುವುದನ್ನು ಇದು ತಡೆಯುತ್ತದೆ."
        })

    # General Routine (Normal weather / Transitional)
    else:
        advisories.append({
            "id": "adv_scouting_01",
            "date": today,
            "category": "Field Scouting",
            "category_kn": "ತೋಟ ಪರಿಶೀಲನೆ",
            "importance": "Medium",
            "crop": "Coconut, Arecanut",
            "crop_kn": "ತೆಂಗು, ಅಡಿಕೆ",
            "title_en": "Inspect Crown for Rhinoceros Beetle & Red Palm Weevil",
            "title_kn": "ತೆಂಗಿನ ಸುಳಿಯಲ್ಲಿ ಕಪ್ಪು ಜೀರುಂಡೆ ಬಾಧೆಯನ್ನು ಪರೀಕ್ಷಿಸಿ",
            "task_en": "Examine top spear leaves for V-shaped cuts. Place pheromone traps or naphthalene balls in leaf axils.",
            "task_kn": "ಸುಳಿ ಎಲೆಗಳಲ್ಲಿ ವಿ-ಆಕಾರದ ಕಡಿತವಿದೆಯೇ ಎಂದು ಗಮನಿಸಿ. ಮರದ ಗರಿಗಳ ಸಂದಿಯಲ್ಲಿ ಕರ್ಪೂರದ ಉಂಡೆಗಳನ್ನು ಇಡಿ.",
            "reason_en": "Moderate weather is conducive for adult beetle movement and infestation.",
            "reason_kn": "ಸಾಧಾರಣ ವಾತಾವರಣದಲ್ಲಿ ಜೀರುಂಡೆಗಳ ಸಂಚಾರ ಹೆಚ್ಚಾಗಿ ಸುಳಿ ಹಾಳಾಗಬಹುದು."
        })
        advisories.append({
            "id": "adv_harvest_drying_01",
            "date": tomorrow,
            "category": "Drying & Post-Harvest",
            "category_kn": "ಒಣಗಿಸುವಿಕೆ ಮತ್ತು ಕೊಯ್ಲೋತ್ತರ",
            "importance": "High",
            "crop": "Arecanut, Cocoa",
            "crop_kn": "ಅಡಿಕೆ, ಕೋಕೋ",
            "title_en": "Sun-Drying Yard Preparation",
            "title_kn": "ಅಡಿಕೆ ಹಾಗೂ ಕೋಕೋ ಒಣಗಿಸಲು ಕಣ ಸಿದ್ಧಪಡಿಸಿ",
            "task_en": "Clear concrete drying yards or tarpaulins to sun-dry harvested ripe arecanuts and fermented cocoa beans.",
            "task_kn": "ಕೊಯ್ಲು ಮಾಡಿದ ಅಡಿಕೆ ಹಾಗೂ ಹುದುಗಿಸಿದ ಕೋಕೋ ಬೀಜಗಳನ್ನು ಒಣಗಿಸಲು ಟಾರ್ಪಾಲಿನ್ ಅಥವಾ ಒಣಗಿಸುವ ಕಣವನ್ನು ಸಿದ್ಧವಾಗಿಡಿ.",
            "reason_en": f"Favorable sunshine hours and low rain probability ({precipitation_prob:.0f}%) ensure optimal drying.",
            "reason_kn": f"ಉತ್ತಮ ಬಿಸಿಲು ಮತ್ತು ಕಡಿಮೆ ಮಳೆ ಮುನ್ಸೂಚನೆ ({precipitation_prob:.0f}%) ಇರುವುದರಿಂದ ಒಣಗಿಸಲು ಸೂಕ್ತ."
        })

    # Filter by selected crop if requested
    if selected_crop and selected_crop != "All":
        filtered = [a for a in advisories if selected_crop.lower() in a["crop"].lower() or "all" in a["crop"].lower()]
        return filtered if filtered else advisories

    return advisories
