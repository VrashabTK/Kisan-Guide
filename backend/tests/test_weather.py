# Weather tests for Dakshina Kannada
from backend.app.services.weather_service import process_weather_data, get_taluk_coords

def test_taluk_geolocation_validity():
    coords = get_taluk_coords("Bantwal")
    assert 12.0 < coords["lat"] < 14.0
    assert 74.0 < coords["lon"] < 76.0
    assert coords["zone"] is not None

def test_process_weather_data_alert_triggers():
    # Synthetic weather snapshot with thunderstorm WMO code 95 and heavy rainfall
    raw_synthetic = {
        "current": {
            "temperature_2m": 29.5,
            "apparent_temperature": 34.0,
            "relative_humidity_2m": 88.0,
            "rain": 45.0,
            "precipitation": 45.0,
            "weather_code": 95,
            "cloud_cover": 90.0,
            "pressure_msl": 1005.0,
            "wind_speed_10m": 50.0,
            "wind_direction_10m": 260.0
        },
        "hourly": {
            "time": ["2026-11-16T12:00", "2026-11-16T13:00"],
            "temperature_2m": [29.5, 28.0],
            "relative_humidity_2m": [88.0, 90.0],
            "precipitation_probability": [90, 85],
            "precipitation": [45.0, 30.0],
            "weather_code": [95, 95]
        },
        "daily": {
            "time": ["2026-11-16", "2026-11-17"],
            "temperature_2m_max": [31.0, 30.0],
            "temperature_2m_min": [24.0, 23.5],
            "precipitation_sum": [75.0, 40.0],
            "precipitation_probability_max": [95, 80],
            "uv_index_max": [6.0, 5.5],
            "weather_code": [95, 65]
        }
    }

    processed = process_weather_data(raw_synthetic, "Mangaluru")
    assert processed["taluk"] == "Mangaluru"
    assert processed["current"]["temperature"] == 29.5
    
    # Must detect both thunderstorm and heavy rain alerts
    alert_categories = [a["category"] for a in processed["alerts"]]
    assert "Thunderstorm" in alert_categories
    assert "Heavy Rainfall" in alert_categories
    assert "High Wind" in alert_categories
