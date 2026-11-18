"""
AI Agricultural & Storage Assistant Service.
Connects to Google Gemini API (or OpenAI compatible) with strict agricultural guardrails.
Includes automatic fallback to verified agronomic rules if key is unconfigured or offline.
"""

import json
import logging
import httpx
from typing import Dict, Any, Optional
from backend.app.core.config import settings
from backend.app.agricultural_rules.crops import CROP_PROFILES
from backend.app.agricultural_rules.storage import STORAGE_PROFILES

logger = logging.getLogger("kissan_guide.ai")

SYSTEM_PROMPT_STORAGE = """You are an expert Agricultural Post-Harvest Specialist for Dakshina Kannada (DK), Karnataka, India.
Your scope is strictly limited to 4 crops: Coconut, Rice (Paddy), Arecanut, and Cocoa.

CRITICAL INSTRUCTIONS:
1. Provide practical, farmer-friendly advice in both English and Kannada.
2. NEVER invent exact storage durations or market prices.
3. NEVER prescribe dangerous chemical dosages or unapproved pesticides.
4. Base recommendations on verified tropical post-harvest science (aeration, moisture control <10% for arecanut, <14% for paddy, <8% for cocoa, <6% for copra).
5. Address issues like dampness, slight spoilage, or improper bags directly.
6. Return your response STRICTLY as valid JSON matching the specified schema.
"""

async def generate_ai_storage_suggestions(
    crop: str,
    harvest_date: str,
    storage_method: str,
    crop_condition: str,
    taluk: str,
    weather_summary: Dict[str, Any],
    rule_evaluation: Dict[str, Any],
    language: str = "en"
) -> Dict[str, Any]:
    """
    Generates AI-powered storage advice with rule-based fallback.
    """
    crop_profile = STORAGE_PROFILES.get(crop, STORAGE_PROFILES["Coconut"])

    # If AI_API_KEY is not configured, return high-quality verified rule-based guidance
    if not settings.AI_API_KEY:
        return _generate_rule_based_ai_fallback(
            crop, storage_method, crop_condition, taluk, rule_evaluation, language
        )

    # Call Gemini API
    try:
        user_prompt = f"""
Farmer Input:
- Crop: {crop} ({crop_profile['name_kn']})
- Location: {taluk}, Dakshina Kannada
- Harvest Date: {harvest_date} (Days elapsed: {rule_evaluation.get('days_elapsed', 0)})
- Storage Method: {storage_method}
- Condition: {crop_condition}
- Ambient Weather: {weather_summary.get('temperature', 28)}°C, Humidity: {weather_summary.get('humidity', 75)}%
- Rule Evaluation: Suitability is '{rule_evaluation.get('suitability')}', Moisture Risk: '{rule_evaluation.get('risks', {}).get('moisture')}', Spoilage Risk: '{rule_evaluation.get('risks', {}).get('spoilage')}'

Provide actionable recommendations:
1. Immediate action to improve storage and avert spoilage.
2. What to do if the crop is damp or slightly damaged.
3. Ventilation, moisture reduction, and pest barrier steps.
4. Explanations in both English and Kannada.

Format as JSON:
{{
  "ai_generated": true,
  "summary_en": "concise farmer advice in English",
  "summary_kn": "ಸರಳ ಕನ್ನಡದಲ್ಲಿ ಸ್ಪಷ್ಟ ಸಲಹೆ",
  "action_steps_en": ["step 1", "step 2", "step 3"],
  "action_steps_kn": ["ಕ್ರಮ 1", "ಕ್ರಮ 2", "ಕ್ರಮ 3"],
  "moisture_management_en": "advice",
  "moisture_management_kn": "ತೇವಾಂಶ ನಿರ್ವಹಣಾ ಸಲಹೆ",
  "pest_prevention_en": "advice",
  "pest_prevention_kn": "ಕೀಟ ನಿಯಂತ್ರಣ ಸಲಹೆ",
  "disclaimer": "AI recommendations are supplementary to standard post-harvest guidelines."
}}
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{settings.AI_MODEL}:generateContent?key={settings.AI_API_KEY}"
        payload = {
            "contents": [
                {"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT_STORAGE}\n\n{user_prompt}"}]}
            ],
            "generationConfig": {
                "temperature": 0.3,
                "response_mime_type": "application/json"
            }
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code == 200:
                result_json = resp.json()
                text_content = result_json["candidates"][0]["content"]["parts"][0]["text"]
                parsed = json.loads(text_content)
                parsed["source"] = "Gemini AI Agricultural Model"
                return parsed
            else:
                logger.warning(f"Gemini API returned status {resp.status_code}: {resp.text}")
    except Exception as e:
        logger.error(f"Error calling AI API: {e}")

    # Fallback if API fails or network unavailable
    return _generate_rule_based_ai_fallback(
        crop, storage_method, crop_condition, taluk, rule_evaluation, language, error=True
    )

def _generate_rule_based_ai_fallback(
    crop: str,
    storage_method: str,
    crop_condition: str,
    taluk: str,
    rule_evaluation: Dict[str, Any],
    language: str,
    error: bool = False
) -> Dict[str, Any]:
    profile = STORAGE_PROFILES.get(crop, STORAGE_PROFILES["Coconut"])
    crop_kn = profile["name_kn"]

    if crop_condition in ["Damp", "Slightly spoiled"]:
        action_en = [
            f"Immediately unload {crop} from bags or dark room and spread thinly on clean tarpaulins in open sun.",
            "Inspect and manually separate any mouldy or blackened pieces to halt cross-contamination.",
            f"Do not bag {crop} until moisture content drops below safe storage thresholds."
        ]
        action_kn = [
            f"{crop_kn} ಬೆಳೆಯನ್ನು ಚೀಲದಿಂದ ಹೊರತೆಗೆದು ಸ್ವಚ್ಛ ಟಾರ್ಪಾಲಿನ್ ಮೇಲೆ ಬಿಸಿಲಿನಲ್ಲಿ ತೆಳುವಾಗಿ ಹರಡಿ.",
            "ಶಿಲೀಂಧ್ರ ಅಥವಾ ಬೂಷ್ಟು ಹತ್ತಿದ ಭಾಗಗಳನ್ನು ತಕ್ಷಣ ಆರಿಸಿ ಪ್ರತ್ಯೇಕಿಸಿ.",
            "ತೇವಾಂಶವು ಸುರಕ್ಷಿತ ಮಟ್ಟಕ್ಕೆ ಇಳಿಯುವವರೆಗೆ ಚೀಲಗಳಲ್ಲಿ ತುಂಬಬೇಡಿ."
        ]
    elif storage_method == "Closed container":
        action_en = [
            f"Cease storing {crop} in airtight containers immediately. Natural respiration produces condensation and rapid decay.",
            "Transfer produce into breathable, clean jute (gunny) bags.",
            "Keep bags on wooden dunnage racks at least 30 cm above the ground."
        ]
        action_kn = [
            f"{crop_kn} ಬೆಳೆಯನ್ನು ಗಾಳಿಯಾಡದ ಮುಚ್ಚಿದ ಡಬ್ಬಗಳಲ್ಲಿ ಇಡಬೇಡಿ; ಇದರಿಂದ ಉಸಿರಾಟದ ನೀರಿನ ಹನಿಗಳು ಶೇಖರವಾಗಿ ಬೇಗನೆ ಕೊಳೆಯುತ್ತದೆ.",
            "ಗಾಳಿಯಾಡುವ ಶುದ್ಧ ಗೋಣಿ ಚೀಲಗಳಿಗೆ ವರ್ಗಾಯಿಸಿ.",
            "ನೆಲದಿಂದ ಕನಿಷ್ಠ 30 ಸೆಂ.ಮೀ ಎತ್ತರದ ಮರದ ಹಲಗೆಯ ಮೇಲೆ ಚೀಲಗಳನ್ನು ಇಡಿ."
        ]
    else:
        action_en = [
            f"Maintain storage room temperature below 28°C and keep windows screened with insect-proof wire mesh.",
            "Elevate gunny stacks 50 cm away from walls to avert moisture seepage from coastal rain.",
            "Conduct routine weekly inspection for grain weevils and fungal growth."
        ]
        action_kn = [
            "ಉಗ್ರಾಣದ ತಾಪಮಾನ 28°C ಗಿಂತ ಕಡಿಮೆಯಿರುವಂತೆ ನೋಡಿಕೊಳ್ಳಿ ಹಾಗೂ ಕಿಟಕಿಗಳಿಗೆ ಜಾಲರಿ ಅಳವಡಿಸಿ.",
            "ಮಳೆಯಿಂದ ಗೋಡೆಗಳಲ್ಲಿ ಬರುವ ತೇವ ತಾಗದಂತೆ ಗೋಡೆಯಿಂದ 50 ಸೆಂ.ಮೀ ಅಂತರದಲ್ಲಿ ಚೀಲಗಳನ್ನು ಜೋಡಿಸಿ.",
            "ಪ್ರತಿ ವಾರ ಕೀಟ ಅಥವಾ ಶಿಲೀಂಧ್ರ ಬಾಧೆಯ ಬಗ್ಗೆ ಪರಿಶೀಲನೆ ನಡೆಸಿ."
        ]

    return {
        "ai_generated": False,
        "is_fallback": True,
        "source": "Agronomic Expert Rules (AI Service Offline/Fallback)",
        "notice": "AI engine is currently operating in verified expert rule mode." if not error else "Live AI service temporarily unavailable; displaying verified agricultural storage guidelines.",
        "summary_en": f"Verified storage plan for {crop} under '{storage_method}' with condition '{crop_condition}'.",
        "summary_kn": f"'{storage_method}' ವಿಧಾನ ಮತ್ತು '{crop_condition}' ಸ್ಥಿತಿಯಲ್ಲಿ {crop_kn} ಬೆಳೆಯ ಪರಿಶೀಲನಾ ವರದಿ.",
        "action_steps_en": action_en,
        "action_steps_kn": action_kn,
        "moisture_management_en": f"Keep {crop} environment at {profile['humidity_threshold']}. Aerate during sunny midday hours.",
        "moisture_management_kn": f"ತೇವಾಂಶವನ್ನು {profile['humidity_threshold']} ಮಟ್ಟದಲ್ಲಿಡಿ. ಬಿಸಿಲಿರುವ ಸಮಯದಲ್ಲಿ ಕಿಟಕಿ ತೆರೆದು ಗಾಳಿಯಾಡಲು ಬಿಡಿ.",
        "pest_prevention_en": "Use clean, disinfected gunny bags. Sprinkle neem powder around pallet legs.",
        "pest_prevention_kn": "ಸ್ವಚ್ಛ ಗೋಣಿ ಚೀಲ ಬಳಸಿ, ಮರದ ಹಲಗೆಯ ಕಾಲಿನ ಸುತ್ತ ಬೇವಿನ ಪುಡಿ ಹಾಕಿ ಕೀಟಗಳನ್ನು ತಡೆಯಿರಿ.",
        "disclaimer": "Based on certified post-harvest agricultural practices for Dakshina Kannada."
    }
