import sys
import os

# Add root directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.tests.test_crops import (
    test_dakshina_kannada_taluks,
    test_supported_crops_scope,
    test_high_water_rice_recommendation,
    test_low_water_penalizes_rice
)
from backend.tests.test_storage import (
    test_storage_profiles_complete,
    test_suitable_arecanut_storage,
    test_unsuitable_closed_container_penalized
)
from backend.tests.test_weather import (
    test_taluk_geolocation_validity,
    test_process_weather_data_alert_triggers
)
from backend.tests.test_api import (
    test_crop_recommendation_endpoint,
    test_weather_endpoints,
    test_storage_recommendation_endpoint,
    test_saved_items_authenticated_flow,
    test_profile_update_flow
)
from backend.tests.test_auth_crop import (
    test_identifier_normalization,
    test_database_registration_and_duplicate_prevention,
    test_database_authentication_and_rate_limiting,
    test_global_crop_preference_synchronization,
    test_api_auth_and_crop_routes
)

def run_all_tests():
    tests = [
        ("Crops: Taluks definition (9 DK Taluks)", test_dakshina_kannada_taluks),
        ("Crops: Supported crops scope (Coconut, Rice, Arecanut, Cocoa)", test_supported_crops_scope),
        ("Crops: High water Rice recommendation", test_high_water_rice_recommendation),
        ("Crops: Low water penalization for Rice", test_low_water_penalizes_rice),
        ("Storage: Profiles complete for 4 crops", test_storage_profiles_complete),
        ("Storage: Suitable Arecanut storage in Jute bag", test_suitable_arecanut_storage),
        ("Storage: Closed container penalty for fresh produce", test_unsuitable_closed_container_penalized),
        ("Weather: Taluk geolocation validation", test_taluk_geolocation_validity),
        ("Weather: Alert triggers detection (Thunderstorm, Rain, Wind)", test_process_weather_data_alert_triggers),
        ("API: Crop recommendation endpoint", test_crop_recommendation_endpoint),
        ("API: Weather forecast and advisory endpoints", test_weather_endpoints),
        ("API: Storage recommendation endpoint", test_storage_recommendation_endpoint),
        ("API: Authenticated saved items flow", test_saved_items_authenticated_flow),
        ("API: Profile update and retrieval flow", test_profile_update_flow),
        ("Auth: Email & Mobile normalization", test_identifier_normalization),
        ("Auth: Database registration & duplicate rejection", test_database_registration_and_duplicate_prevention),
        ("Auth: Database authentication & rate-limiting", test_database_authentication_and_rate_limiting),
        ("Crops: Global crop preference persistence", test_global_crop_preference_synchronization),
        ("API: Auth signup/login & crop synchronization", test_api_auth_and_crop_routes),
    ]

    passed = 0
    failed = 0
    print("\n" + "="*65, flush=True)
    print("RUNNING KISSAN GUIDE BACKEND AUTOMATED TEST SUITE", flush=True)
    print("="*65, flush=True)

    for name, test_func in tests:
        print(f"Executing: {name} ...", flush=True)
        try:
            test_func()
            print(f"  [PASS] {name}", flush=True)
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}", flush=True)
            failed += 1

    print("="*65, flush=True)
    print(f"RESULTS: {passed} PASSED, {failed} FAILED out of {len(tests)} tests.", flush=True)
    print("="*65 + "\n", flush=True)

    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    run_all_tests()
