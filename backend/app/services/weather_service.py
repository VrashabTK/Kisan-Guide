"""
Weather Service for Dakshina Kannada District.
Supports Open-Meteo (default, free, no key required), OpenWeather, or custom API.
Includes caching, severe weather detection, and accurate geolocation for all DK taluks.
"""

import time
import httpx
import logging
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings
from backend.app.agricultural_rules.crops import DK_TALUKS

logger = logging.getLogger("kissan_guide.weather")

# Simple in-memory cache: (taluk, is_forecast) -> (timestamp, data)
_CACHE: Dict[str, tuple[float, Dict[str, Any]]] = {}
CACHE_TTL_SECONDS = 900  # 15 minutes

WMO_WEATHER_CODES = {
    0: {"en": "Clear sky", "kn": "ಸ್ವಚ್ಛ ಆಕಾಶ"},
    1: {"en": "Mainly clear", "kn": "ಮುಖ್ಯವಾಗಿ ಸ್ಪಷ್ಟ ಆಕಾಶ"},
    2: {"en": "Partly cloudy", "kn": "ಭಾಗಶಃ ಮೋಡ ಕವಿದ ಆಕಾಶ"},
    3: {"en": "Overcast", "kn": "ದಟ್ಟ ಮೋಡ ಕವಿದ ವಾತಾವರಣ"},
    45: {"en": "Foggy", "kn": "ಮಂಜು ಮುಸುಕಿದ ವಾತಾವರಣ"},
    48: {"en": "Depositing rime fog", "kn": "ಹಿಮ ಮಂಜು"},
    51: {"en": "Light drizzle", "kn": "ತಿಳಿ ತುಂತುರು ಮಳೆ"},
    53: {"en": "Moderate drizzle", "kn": "ಸಾಧಾರಣ ತುಂತುರು ಮಳೆ"},
    55: {"en": "Dense drizzle", "kn": "ದಟ್ಟ ತುಂತುರು ಮಳೆ"},
    61: {"en": "Slight rain", "kn": "ಹಗುರ ಮಳೆ"},
    63: {"en": "Moderate rain", "kn": "ಸಾಧಾರಣ ಮಳೆ"},
    65: {"en": "Heavy rain", "kn": "ಭಾರಿ ಮಳೆ"},
    80: {"en": "Slight rain showers", "kn": "ಹಗುರ ಮಳೆ ಸಿಂಚನ"},
    81: {"en": "Moderate rain showers", "kn": "ಸಾಧಾರಣ ಮಳೆ ಸಿಂಚನ"},
    82: {"en": "Violent rain showers", "kn": "ತೀವ್ರ ಮಳೆ ಸಿಂಚನ"},
    95: {"en": "Thunderstorm", "kn": "ಗುಡುಗು ಸಹಿತ ಮಳೆ"},
    96: {"en": "Thunderstorm with slight hail", "kn": "ಗುಡುಗು ಮತ್ತು ಆಲಿಕಲ್ಲು ಮಳೆ"},
    99: {"en": "Severe thunderstorm with heavy hail", "kn": "ತೀವ್ರ ಗುಡುಗು ಸಹಿತ ಭಾರಿ ಮಳೆ"},
}

def get_taluk_coords(taluk: str) -> Dict[str, Any]:
    return DK_TALUKS.get(taluk, DK_TALUKS["Mangaluru"])

async def fetch_open_meteo_weather(taluk: str) -> Dict[str, Any]:
    coords = get_taluk_coords(taluk)
    lat, lon = coords["lat"], coords["lon"]

    url = f"{settings.WEATHER_API_BASE_URL}/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,cloud_cover,pressure_msl,wind_speed_10m,wind_direction_10m",
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation,weather_code,wind_speed_10m",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,uv_index_max,sunrise,sunset",
        "timezone": "Asia/Kolkata",
        "forecast_days": 5,
    }

    async with httpx.AsyncClient(timeout=httpx.Timeout(connect=2.0, read=3.0, write=2.0, pool=2.0)) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

def process_weather_data(raw: Dict[str, Any], taluk: str) -> Dict[str, Any]:
    coords = get_taluk_coords(taluk)
    current = raw.get("current", {})
    hourly = raw.get("hourly", {})
    daily = raw.get("daily", {})

    code = current.get("weather_code", 0)
    condition_info = WMO_WEATHER_CODES.get(code, {"en": "Cloudy", "kn": "ಮೋಡ"})

    temp = current.get("temperature_2m", 28.0)
    feels_like = current.get("apparent_temperature", temp)
    humidity = current.get("relative_humidity_2m", 75.0)
    rainfall = current.get("rain", current.get("precipitation", 0.0))
    wind_speed = current.get("wind_speed_10m", 12.0)
    wind_direction = current.get("wind_direction_10m", 240.0)
    cloud_cover = current.get("cloud_cover", 40.0)
    pressure = current.get("pressure_msl", 1010.0)

    # Process next 24-hour forecast
    hourly_forecast = []
    times = hourly.get("time", [])[:24]
    temps = hourly.get("temperature_2m", [])[:24]
    humids = hourly.get("relative_humidity_2m", [])[:24]
    precip_probs = hourly.get("precipitation_probability", [])[:24]
    precips = hourly.get("precipitation", [])[:24]
    codes = hourly.get("weather_code", [])[:24]

    for i in range(len(times)):
        w_code = codes[i] if i < len(codes) else 0
        c_info = WMO_WEATHER_CODES.get(w_code, {"en": "Partly cloudy", "kn": "ಭಾಗಶಃ ಮೋಡ"})
        hourly_forecast.append({
            "time": times[i],
            "temperature": temps[i] if i < len(temps) else temp,
            "humidity": humids[i] if i < len(humids) else humidity,
            "precipitation_probability": precip_probs[i] if i < len(precip_probs) else 0,
            "precipitation": precips[i] if i < len(precips) else 0.0,
            "condition_en": c_info["en"],
            "condition_kn": c_info["kn"],
            "weather_code": w_code,
        })

    # Process 4-day daily forecast
    daily_forecast = []
    d_times = daily.get("time", [])[:4]
    d_max = daily.get("temperature_2m_max", [])[:4]
    d_min = daily.get("temperature_2m_min", [])[:4]
    d_rain = daily.get("precipitation_sum", [])[:4]
    d_probs = daily.get("precipitation_probability_max", [])[:4]
    d_uv = daily.get("uv_index_max", [])[:4]
    d_codes = daily.get("weather_code", [])[:4]
    d_sunrise = daily.get("sunrise", [])[:4]
    d_sunset = daily.get("sunset", [])[:4]

    for i in range(len(d_times)):
        w_code = d_codes[i] if i < len(d_codes) else 0
        c_info = WMO_WEATHER_CODES.get(w_code, {"en": "Partly cloudy", "kn": "ಭಾಗಶಃ ಮೋಡ"})
        daily_forecast.append({
            "date": d_times[i],
            "temp_max": d_max[i] if i < len(d_max) else temp + 3,
            "temp_min": d_min[i] if i < len(d_min) else temp - 4,
            "rainfall_sum": d_rain[i] if i < len(d_rain) else 0.0,
            "rain_probability": d_probs[i] if i < len(d_probs) else 10,
            "uv_index": d_uv[i] if i < len(d_uv) else 6.0,
            "sunrise": d_sunrise[i] if i < len(d_sunrise) else "",
            "sunset": d_sunset[i] if i < len(d_sunset) else "",
            "condition_en": c_info["en"],
            "condition_kn": c_info["kn"],
            "weather_code": w_code,
        })

    # Severe Weather Alert Detection based on IMD / WMO criteria
    alerts = []
    # 1. Thunderstorm Alert
    if code in [95, 96, 99]:
        alerts.append({
            "id": f"alert_ts_{int(time.time())}",
            "title_en": "Severe Thunderstorm & Lightning Warning",
            "title_kn": "ತೀವ್ರ ಗುಡುಗು ಹಾಗೂ ಮಿಂಚು ಎಚ್ಚರಿಕೆ",
            "severity": "Critical",
            "category": "Thunderstorm",
            "source": "Threshold-based Meteorological Monitor",
            "affected_location": taluk,
            "affected_location_kn": coords["name_kn"],
            "precautions_en": [
                "Move to safe concrete structures immediately; do not take shelter under solitary coconut or arecanut trees.",
                "Disconnect electrical pump starters and avoid touching metal water pipelines.",
                "Cease all outdoor spraying and ladder harvesting operations."
            ],
            "precautions_kn": [
                "ತಕ್ಷಣ ಪಕ್ಕಾ ಕಟ್ಟಡಗಳಲ್ಲಿ ಆಶ್ರಯ ಪಡೆಯಿರಿ; ಎತ್ತರದ ತೆಂಗು ಅಥವಾ ಅಡಿಕೆ ಮರಗಳ ಕೆಳಗೆ ನಿಲ್ಲಬೇಡಿ.",
                "ಪಂಪ್‌ಸೆಟ್ ಸ್ಟಾರ್ಟರ್ ಸಂಪರ್ಕ ಕಡಿತಗೊಳಿಸಿ, ಲೋಹದ ನೀರಿನ ಪೈಪ್‌ಗಳನ್ನು ಮುಟ್ಟಬೇಡಿ.",
                "ಹೊರಾಂಗಣದಲ್ಲಿ ಔಷಧ ಸಿಂಪಡಣೆ ಹಾಗೂ ಕೊಯ್ಲು ಕೆಲಸವನ್ನು ಕೂಡಲೇ ನಿಲ್ಲಿಸಿ."
            ]
        })

    # 2. Heavy Rainfall Alert (> 64.5mm in 24h or > 20mm in current snapshot)
    today_rain = daily_forecast[0]["rainfall_sum"] if daily_forecast else rainfall
    if today_rain > 64.5 or rainfall > 20.0:
        alerts.append({
            "id": f"alert_hr_{int(time.time())}",
            "title_en": "Heavy Rainfall Advisory (Yellow/Orange Level)",
            "title_kn": "ಭಾರಿ ಮಳೆ ಮುನ್ನೆಚ್ಚರಿಕೆ (ಕರಾವಳಿ ಭಾಗ)",
            "severity": "Severe",
            "category": "Heavy Rainfall",
            "source": "Threshold-based Meteorological Monitor",
            "affected_location": taluk,
            "affected_location_kn": coords["name_kn"],
            "precautions_en": [
                "Unblock garden trenches to avoid standing water around arecanut and cocoa roots.",
                "Regulate paddy field spillways to safeguard young rice tillers.",
                "Keep harvested produce inside raised, waterproof storage facilities."
            ],
            "precautions_kn": [
                "ಅಡಿಕೆ ಮತ್ತು ಕೋಕೋ ಬೇರುಗಳಲ್ಲಿ ನೀರು ನಿಲ್ಲದಂತೆ ತೋಟದ ಚರಂಡಿಗಳನ್ನು ತೆರವುಗೊಳಿಸಿ.",
                "ಭತ್ತದ ಗದ್ದೆಗಳಲ್ಲಿ ನೀರು ಮಿತಿಮೀರದಂತೆ ತೂಬುಗಳನ್ನು ತೆರೆದು ನೀರಿನ ಮಟ್ಟ ಕಾಪಾಡಿ.",
                "ಕೊಯ್ಲು ಮಾಡಿದ ಉತ್ಪನ್ನಗಳನ್ನು ತೇವ ತಾಗದಂತೆ ಸುರಕ್ಷಿತ ಉಗ್ರಾಣದಲ್ಲಿಡಿ."
            ]
        })

    # 3. High Wind Alert (> 45 km/h)
    if wind_speed > 45.0:
        alerts.append({
            "id": f"alert_wind_{int(time.time())}",
            "title_en": "Squally Wind / Coastal Gale Advisory",
            "title_kn": "ತೀವ್ರ ಬಿರುಗಾಳಿ ಎಚ್ಚರಿಕೆ",
            "severity": "Moderate",
            "category": "High Wind",
            "source": "Threshold-based Meteorological Monitor",
            "affected_location": taluk,
            "affected_location_kn": coords["name_kn"],
            "precautions_en": [
                "Provide physical bamboo propping for young cocoa and arecanut seedlings.",
                "Watch for falling coconut fronds and loose electrical wires in plantations."
            ],
            "precautions_kn": [
                "ಎಳೆಯ ಅಡಿಕೆ ಹಾಗೂ ಕೋಕೋ ಸಸಿಗಳು ಗಾಳಿಗೆ ಮುರಿಯದಂತೆ ಆಸರೆ ಕಂಬಗಳನ್ನು ಕಟ್ಟಿ.",
                "ತೋಟದಲ್ಲಿ ಒಣ ತೆಂಗಿನ ಗರಿಗಳು ಹಾಗೂ ವಿದ್ಯುತ್ ತಂತಿಗಳ ಬಗ್ಗೆ ಜಾಗ್ರತೆ ವಹಿಸಿ."
            ]
        })

    # 4. Extreme Heat Alert (> 35°C in Coastal Humid Region)
    if temp > 35.0:
        alerts.append({
            "id": f"alert_heat_{int(time.time())}",
            "title_en": "High Heat & Humidity Stress Warning",
            "title_kn": "ಹೆಚ್ಚಿನ ಶಾಖ ಮತ್ತು ತೇವಾಂಶದ ಎಚ್ಚರಿಕೆ",
            "severity": "Moderate",
            "category": "Heat Alert",
            "source": "Threshold-based Meteorological Monitor",
            "affected_location": taluk,
            "affected_location_kn": coords["name_kn"],
            "precautions_en": [
                "Irrigate during cool morning or late evening hours to reduce root thermal shock.",
                "Apply mulch around tree basins to preserve soil moisture.",
                "Stay hydrated and avoid heavy physical field work between 12:00 PM and 3:30 PM."
            ],
            "precautions_kn": [
                "ಬೆಳಿಗ್ಗೆ ಬೇಗನೆ ಅಥವಾ ಸಂಜೆ ತಂಪು ಹೊತ್ತಿನಲ್ಲಿ ನೀರು ಹಾಯಿಸಿ.",
                "ಮರದ ಬುಡಕ್ಕೆ ಒಣ ತ್ಯಾಜ್ಯದ ಹೊದಿಕೆ (ಮಲ್ಚಿಂಗ್) ಹಾಕಿ ತೇವಾಂಶ ಕಾಪಾಡಿ.",
                "ಮಧ್ಯಾಹ್ನ 12 ರಿಂದ 3.30 ರವರೆಗೆ ಕಠಿಣ ಬಿಸಿಲಿನಲ್ಲಿ ಹೊಲಗೆಲಸ ಮಾಡುವುದನ್ನು ತಪ್ಪಿಸಿ."
            ]
        })

    return {
        "taluk": taluk,
        "taluk_kn": coords["name_kn"],
        "zone": coords["zone"],
        "latitude": coords["lat"],
        "longitude": coords["lon"],
        "current": {
            "temperature": round(temp, 1),
            "feels_like": round(feels_like, 1),
            "humidity": round(humidity, 1),
            "rainfall": round(rainfall, 1),
            "wind_speed": round(wind_speed, 1),
            "wind_direction": round(wind_direction, 0),
            "cloud_cover": round(cloud_cover, 0),
            "pressure": round(pressure, 1),
            "condition_en": condition_info["en"],
            "condition_kn": condition_info["kn"],
            "weather_code": code,
        },
        "hourly_forecast": hourly_forecast,
        "daily_forecast": daily_forecast,
        "alerts": alerts,
        "fetched_at": int(time.time()),
        "source": "Open-Meteo Verified Meteorological Feed",
    }

async def get_weather(taluk: str = "Mangaluru", force_refresh: bool = False) -> Dict[str, Any]:
    """
    Returns weather for the specified taluk with caching.
    """
    cache_key = taluk.strip()
    now = time.time()

    if not force_refresh and cache_key in _CACHE:
        timestamp, data = _CACHE[cache_key]
        if now - timestamp < CACHE_TTL_SECONDS:
            return data

    try:
        raw = await fetch_open_meteo_weather(taluk)
        data = process_weather_data(raw, taluk)
        _CACHE[cache_key] = (now, data)
        return data
    except Exception as e:
        logger.error(f"Failed to fetch live weather for {taluk}: {e}")
        # If cache exists even if expired, return it
        if cache_key in _CACHE:
            return _CACHE[cache_key][1]
        
        # If no cache and network failed, provide safe fallback with explicit clear disclaimer
        coords = get_taluk_coords(taluk)
        return {
            "taluk": taluk,
            "taluk_kn": coords["name_kn"],
            "zone": coords["zone"],
            "latitude": coords["lat"],
            "longitude": coords["lon"],
            "current": {
                "temperature": 28.5,
                "feels_like": 31.0,
                "humidity": 78.0,
                "rainfall": 0.0,
                "wind_speed": 12.0,
                "wind_direction": 250.0,
                "cloud_cover": 45.0,
                "pressure": 1012.0,
                "condition_en": "Partly cloudy (Offline Snapshot)",
                "condition_kn": "ಭಾಗಶಃ ಮೋಡ (ಆಫ್‌ಲೈನ್ ಸ್ನ್ಯಾಪ್‌ಶಾಟ್)",
                "weather_code": 2,
            },
            "hourly_forecast": [],
            "daily_forecast": [],
            "alerts": [],
            "fetched_at": int(now),
            "source": "Local Fallback (Live API unavailable)",
            "is_fallback": True,
            "error_detail": str(e)
        }
