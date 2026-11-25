"""
Agricultural Lifecycles and Management Knowledge Base for Dakshina Kannada.
Strictly focused on the 4 supported crops:
1. Rice (Paddy) - Seasonal crop (~110-135 days)
2. Coconut - Perennial palm
3. Arecanut - Perennial plantation crop
4. Cocoa - Perennial shade / intercrop
"""

from typing import Dict, Any, List, Optional

# ==================== Crop Stage Definitions ====================

CROP_STAGES: Dict[str, List[Dict[str, Any]]] = {
    "Rice": [
        {
            "id": "land_prep",
            "name_en": "Land Preparation",
            "name_kn": "ಭೂಮಿ ಸಿದ್ಧತೆ",
            "start_day": 1,
            "end_day": 12,
            "description_en": "Ploughing, puddling, bund shaping, and applying organic basal manure.",
            "description_kn": "ಉಳುಮೆ, ಕೆಸರು ಮಾಡುವುದು, ಬದು ನಿರ್ಮಾಣ ಮತ್ತು ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಸೇರಿಸುವುದು."
        },
        {
            "id": "nursery",
            "name_en": "Nursery & Sowing",
            "name_kn": "ಸಸಿಮಡಿ ಮತ್ತು ಬಿತ್ತನೆ",
            "start_day": 1,
            "end_day": 25,
            "description_en": "Seed treatment with Trichoderma/Pseudomonas, raised bed preparation, and healthy seedling raising.",
            "description_kn": "ಬೀಜೋಪಚಾರ, ಏರುಮಡಿ ಸಿದ್ಧತೆ ಮತ್ತು ಆರೋಗ್ಯಕರ ಸಸಿಗಳ ಬೆಳವಣಿಗೆ."
        },
        {
            "id": "transplanting",
            "name_en": "Transplanting / Direct Seeding",
            "name_kn": "ನಾಟಿ / ನೇರ ಬಿತ್ತನೆ",
            "start_day": 20,
            "end_day": 35,
            "description_en": "Transplanting 20-25 day old seedlings with 20x15cm spacing or direct drum seeding in puddled soil.",
            "description_kn": "20-25 ದಿನಗಳ ಸಸಿಗಳನ್ನು ಸೂಕ್ತ ಅಂತರದಲ್ಲಿ ನಾಟಿ ಮಾಡುವುದು ಅಥವಾ ನೇರ ಬಿತ್ತನೆ."
        },
        {
            "id": "vegetative",
            "name_en": "Vegetative Growth",
            "name_kn": "ಸಸ್ಯ ಬೆಳವಣಿಗೆಯ ಹಂತ",
            "start_day": 30,
            "end_day": 55,
            "description_en": "Early tillering, first hand/cono-weeding, and initial nitrogen top-dressing.",
            "description_kn": "ಮೊದಲ ಕಳೆ ಕೀಳುವುದು, ಸಾರಜನಕ ಪೂರೈಕೆ ಮತ್ತು ನೀರಿನ ನಿರ್ವಹಣೆ."
        },
        {
            "id": "tillering",
            "name_en": "Active Tillering",
            "name_kn": "ಚುರುಕಾದ ತೆಂಡೆ ಒಡೆಯುವ ಹಂತ",
            "start_day": 45,
            "end_day": 70,
            "description_en": "Peak tillering, water management at 3-5 cm, pest scouting for stem borer and leaf folder.",
            "description_kn": "ಗರಿಷ್ಠ ತೆಂಡೆ ಬರುವಿಕೆ, 3-5 ಸೆಂ.ಮೀ ನೀರು ನಿಲ್ಲಿಸುವುದು ಮತ್ತು ಕೀಟಗಳ ನಿಗಾ."
        },
        {
            "id": "panicle_initiation",
            "name_en": "Panicle Initiation & Flowering",
            "name_kn": "ತೆನೆ ಮೂಡುವಿಕೆ ಮತ್ತು ಹೂವಾಡುವ ಹಂತ",
            "start_day": 65,
            "end_day": 90,
            "description_en": "Booting, heading, and flowering. Critical water requirement — prevent moisture stress.",
            "description_kn": "ಹೂವಾಡುವ ಮತ್ತು ತೆನೆ ಹೊರಬರುವ ಅತ್ಯಂತ ಸೂಕ್ಷ್ಮ ಹಂತ. ತೇವಾಂಶ ಕೊರತೆಯಾಗದಂತೆ ನೀರು ನಿಲ್ಲಿಸಿ."
        },
        {
            "id": "grain_development",
            "name_en": "Grain Development (Milking/Dough)",
            "name_kn": "ಕಾಳು ತುಂಬುವ ಹಂತ (ಹಾಲು ಮತ್ತು ಗಟ್ಟಿ ಹಂತ)",
            "start_day": 85,
            "end_day": 110,
            "description_en": "Milking to soft-dough stage. Monitor for gundhi bug; keep soil consistently moist.",
            "description_kn": "ತೆನೆಗಳಲ್ಲಿ ಹಾಲು ತುಂಬಿ ಕಾಳು ಗಟ್ಟಿಯಾಗುವ ಹಂತ. ಗಂಧಿ ಕೀಟದ ಹಾವಳಿ ತಡೆಯಿರಿ."
        },
        {
            "id": "ripening",
            "name_en": "Ripening & Maturity",
            "name_kn": "ಕಾಳು ಪಕ್ವತೆ ಮತ್ತು ಬಲಿಯುವ ಹಂತ",
            "start_day": 105,
            "end_day": 125,
            "description_en": "Grains turn golden yellow. Drain field water 10-12 days before harvest to firm soil.",
            "description_kn": "ಕಾಳುಗಳು ಹಳದಿ-ಚಿನ್ನದ ಬಣ್ಣಕ್ಕೆ ತಿರುಗುತ್ತವೆ. ಕೊಯ್ಲಿಗೆ 10-12 ದಿನ ಮುಂಚಿತವಾಗಿ ಗದ್ದೆಯಿಂದ ನೀರು ಬಸಿದುಬಿಡಿ."
        },
        {
            "id": "harvest",
            "name_en": "Harvesting & Threshing",
            "name_kn": "ಕೊಯ್ಲು ಮತ್ತು ಒಕ್ಕಣೆ",
            "start_day": 120,
            "end_day": 140,
            "description_en": "Cutting crop at base, immediate threshing, cleaning, and sun drying to 12-14% moisture.",
            "description_kn": "ಸೂಕ್ತ ಸಮಯದಲ್ಲಿ ಕೊಯ್ಲು ಮಾಡಿ, ಒಕ್ಕಣೆ ಮಾಡಿ, 12-14% ತೇವಾಂಶಕ್ಕೆ ಬಿಸಿಲಿನಲ್ಲಿ ಒಣಗಿಸಿ."
        }
    ],

    "Coconut": [
        {
            "id": "seedling_establishment",
            "name_en": "Seedling Establishment (0 - 1 Year)",
            "name_kn": "ಸಸಿ ಸ್ಥಾಪನೆ (0 - 1 ವರ್ಷ)",
            "start_day": 1,
            "end_day": 365,
            "description_en": "Initial planting in 1m x 1m pits, shade provision, termite prevention, and regular basin watering.",
            "description_kn": "1 ಮೀಟರ್ ಗುಂಡಿಗಳಲ್ಲಿ ನಾಟಿ, ನೆರಳು ಒದಗಿಸುವುದು ಮತ್ತು ಬೇಸಿಗೆಯಲ್ಲಿ ಸತತ ನೀರುಣಿಸುವುದು."
        },
        {
            "id": "juvenile_growth",
            "name_en": "Juvenile Growth (1 - 4 Years)",
            "name_kn": "ಬೆಳೆಯುತ್ತಿರುವ ಹಂತ (1 - 4 ವರ್ಷ)",
            "start_day": 366,
            "end_day": 1460,
            "description_en": "Vigorous vegetative growth, crown formation, collar protection against Rhinoceros beetle, and weed management.",
            "description_kn": "ಗರಿಗಳ ಬೆಳವಣಿಗೆ, ಕಾಂಡದ ದೃಢತೆ, ಕೊಂಬೆ ಮೂತಿ ಕೀಟದ ನಿಯಂತ್ರಣ ಮತ್ತು ಕಳೆ ನಿರ್ವಹಣೆ."
        },
        {
            "id": "pre_bearing",
            "name_en": "Pre-bearing & Early Flowering (5 - 7 Years)",
            "name_kn": "ಮೊದಲ ಹೂಗೊಂಚಲು / ಆರಂಭಿಕ ಕಾಯಿ ಹಂತ (5 - 7 ವರ್ಷ)",
            "start_day": 1461,
            "end_day": 2555,
            "description_en": "Appearance of first spathes/inflorescences, root zone fertilization, and button shed prevention.",
            "description_kn": "ಮೊದಲ ಹೂಗೊಂಚಲು ಬರುವುದು, ಬಟನ್ ಉದುರುವುದನ್ನು ತಡೆಯುವುದು ಮತ್ತು ಸೂಕ್ಷ್ಮ ಪೋಷಕಾಂಶಗಳ ಪೂರೈಕೆ."
        },
        {
            "id": "mature_bearing",
            "name_en": "Mature Bearing Palm (8+ Years)",
            "name_kn": "ಪೂರ್ಣ ಫಲ ನೀಡುವ ಪ್ರೌಢ ಮರ (8+ ವರ್ಷ)",
            "start_day": 2556,
            "end_day": 25000,
            "description_en": "Regular recurring cycles: bi-monthly harvesting rounds, seasonal fertilizer splits (May & Sept), basin mulching, and phytosanitary crown cleaning.",
            "description_kn": "45-60 ದಿನಗಳಿಗೊಮ್ಮೆ ಕಾಯಿ ಕೀಳುವಿಕೆ, ವರ್ಷಕ್ಕೆ ಎರಡು ಬಾರಿ ಗೊಬ್ಬರ ಪೂರೈಕೆ ಮತ್ತು ಗರಿ ಸ್ವಚ್ಛತೆ."
        },
        {
            "id": "senile_rejuvenation",
            "name_en": "Rejuvenation / Senile Palm",
            "name_kn": "ಪುನಶ್ಚೇತನ / ಹಳೆಯ ಮರಗಳ ನಿರ್ವಹಣೆ",
            "start_day": 25001,
            "end_day": 40000,
            "description_en": "Underplanting of improved high-yielding varieties, stem injection if needed, and organic revitalization.",
            "description_kn": "ಹಳೆಯ ಮರಗಳ ನಡುವೆ ಹೊಸ ಅಧಿಕ ಇಳುವರಿಯ ತಳಿಗಳ ನಾಟಿ ಮತ್ತು ಸಾವಯವ ಮರುಪೂರಣ."
        }
    ],

    "Arecanut": [
        {
            "id": "seedling_establishment",
            "name_en": "Seedling Establishment (0 - 1 Year)",
            "name_kn": "ಸಸಿ ಸ್ಥಾಪನೆ (0 - 1 ವರ್ಷ)",
            "start_day": 1,
            "end_day": 365,
            "description_en": "Planting healthy 1-2 year old seedlings at 2.7m x 2.7m spacing with sun-scorch protection on South-West side.",
            "description_kn": "2.7 x 2.7 ಮೀ ಅಂತರದಲ್ಲಿ ನಾಟಿ, ನೈಋತ್ಯ ದಿಕ್ಕಿನಿಂದ ಸುಡುವ ಬಿಸಿಲಿಗೆ ರಕ್ಷಣೆ."
        },
        {
            "id": "young_garden",
            "name_en": "Young Garden Growth (1 - 4 Years)",
            "name_kn": "ಎಳೆಯ ತೋಟದ ಬೆಳವಣಿಗೆ (1 - 4 ವರ್ಷ)",
            "start_day": 366,
            "end_day": 1460,
            "description_en": "Soil building with green manure, drip/basin irrigation during dry months, and digging drainage trenches.",
            "description_kn": "ಹಸಿರೆಲೆ ಗೊಬ್ಬರ, ತೇವಾಂಶ ನಿರ್ವಹಣೆ ಮತ್ತು ಮಳೆಗಾಲಕ್ಕೆ ಮುನ್ನ ಚರಂಡಿ ತೋಡುವುದು."
        },
        {
            "id": "early_bearing",
            "name_en": "Early Bearing (5 - 7 Years)",
            "name_kn": "ಮೊದಲ ಇಳುವರಿ ಹಂತ (5 - 7 ವರ್ಷ)",
            "start_day": 1461,
            "end_day": 2555,
            "description_en": "Emergence of first spadix, prophylactic Bordeaux spray against Koleroga (fruit rot) before monsoon.",
            "description_kn": "ಮೊದಲ ಸಿಂಗಾರ ಮೂಡುವುದು, ಮುಂಗಾರಿಗೆ ಮುನ್ನ ಕೊಳೆರೋಗ ತಡೆಗೆ ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಣೆ."
        },
        {
            "id": "mature_bearing",
            "name_en": "Mature Bearing Garden (8+ Years)",
            "name_kn": "ಪೂರ್ಣ ಇಳುವರಿ ತೋಟ (8+ ವರ್ಷ)",
            "start_day": 2556,
            "end_day": 25000,
            "description_en": "Continuous commercial production: pre-monsoon Koleroga spray, split nutrient doses (May/June and Sept/Oct), organic mulching, and tender/ripe nut harvest.",
            "description_kn": "ಕೊಳೆರೋಗ ನಿಯಂತ್ರಣ, ಮುಂಗಾರು ಪೂರ್ವ ಮತ್ತು ಮುಂಗಾರು ನಂತರದ ರಸಗೊಬ್ಬರ ಪೂರೈಕೆ, ಸಕಾಲಿಕ ಕೊಯ್ಲು."
        }
    ],

    "Cocoa": [
        {
            "id": "seedling_establishment",
            "name_en": "Seedling Establishment (0 - 1 Year)",
            "name_kn": "ಸಸಿ ಸ್ಥಾಪನೆ (0 - 1 ವರ್ಷ)",
            "start_day": 1,
            "end_day": 365,
            "description_en": "Planting under 50% shade of Arecanut or Coconut, staking against wind, and frequent light watering.",
            "description_kn": "ತೆಂಗು ಅಥವಾ ಅಡಿಕೆ ತೋಟದ 50% ನೆರಳಿನಲ್ಲಿ ನಾಟಿ, ಗಾಳಿಗೆ ಆಸರೆ ಮತ್ತು ಹಿತಮಿತ ನೀರುಣಿಸುವಿಕೆ."
        },
        {
            "id": "canopy_development",
            "name_en": "Canopy Formation & Pruning (1 - 3 Years)",
            "name_kn": "ಕವಲು ನಿರ್ಮಾಣ ಮತ್ತು ಸಮರುವಿಕೆ (1 - 3 ವರ್ಷ)",
            "start_day": 366,
            "end_day": 1095,
            "description_en": "Formation pruning at jorquette (fan branches), removing vertical chupons, and keeping stem clean up to 1-1.5 meters.",
            "description_kn": "ಕವಲು ಒಡೆಯುವ ಎತ್ತರದಲ್ಲಿ ಸಮರುವಿಕೆ, ಅನಗತ್ಯ ಜುಟ್ಟು ಕೊಂಬೆಗಳ (ಚುಪೋನ್) ಕತ್ತರಿಸುವಿಕೆ."
        },
        {
            "id": "early_bearing",
            "name_en": "Early Flowering & Pod Formation (3 - 5 Years)",
            "name_kn": "ಆರಂಭಿಕ ಹೂವು ಮತ್ತು ಕಾಯಿ ಹಂತ (3 - 5 ವರ್ಷ)",
            "start_day": 1096,
            "end_day": 1825,
            "description_en": "Cushion flowering, cherelle wilt monitoring, and organic manuring.",
            "description_kn": "ಕಾಂಡದ ಮೇಲೆ ಹೂವು ಅರಳುವುದು, ಎಳೆಯ ಕಾಯಿ ಒಣಗುವಿಕೆ ತಡೆ ಮತ್ತು ಪೋಷಕಾಂಶಗಳ ನಿರ್ವಹಣೆ."
        },
        {
            "id": "mature_bearing",
            "name_en": "Mature Bearing Garden (5+ Years)",
            "name_kn": "ಪೂರ್ಣ ಫಲ ನೀಡುವ ತೋಟ (5+ ವರ್ಷ)",
            "start_day": 1826,
            "end_day": 20000,
            "description_en": "Full yield management: sanitary pruning twice yearly, Black Pod (Phytophthora) management during monsoon, harvesting ripe yellow/orange pods, and wooden box fermentation.",
            "description_kn": "ಕಪ್ಪು ಕಾಯಿ ಕೊಳೆರೋಗ ನಿಯಂತ್ರಣ, ಹಳದಿ-ಕಿತ್ತಳೆ ಬಣ್ಣದ ಬಲಿತ ಕಾಯಿಗಳ ಕೊಯ್ಲು ಮತ್ತು ಪೆಟ್ಟಿಗೆ ಹುದುಗುವಿಕೆ."
        }
    ]
}

# ==================== Core Crop Activity Templates ====================

CROP_ACTIVITIES_KNOWLEDGE_BASE: Dict[str, List[Dict[str, Any]]] = {
    "Rice": [
        {
            "stage_id": "land_prep",
            "title_en": "Primary Ploughing & Bund Repair",
            "title_kn": "ಮೊದಲ ಉಳುಮೆ ಮತ್ತು ಗದ್ದೆಯ ಬದು ದುರಸ್ತಿ",
            "description_en": "Plough the field twice with mouldboard plough to turn over stubbles. Clean and strengthen perimeter bunds to prevent water seepage.",
            "description_kn": "ಹಿಂದಿನ ಬೆಳೆಯ ಉಳಿಕೆಗಳನ್ನು ಮಣ್ಣಿನಲ್ಲಿ ಸೇರಿಸಲು ಉಳುಮೆ ಮಾಡಿ. ನೀರು ಪೋಲಾಗದಂತೆ ಬದುಗಳನ್ನು ಭದ್ರಪಡಿಸಿ.",
            "why_necessary_en": "Improves soil aeration, buries weed seeds, and ensures level water retention across the plot.",
            "why_necessary_kn": "ಮಣ್ಣಿನ ರಚನೆ ಸುಧಾರಿಸುತ್ತದೆ, ಕಳೆಗಳನ್ನು ನಿಯಂತ್ರಿಸುತ್ತದೆ ಮತ್ತು ಗದ್ದೆಯಲ್ಲಿ ನೀರು ಸಮನಾಗಿ ನಿಲ್ಲಲು ನೆರವಾಗುತ್ತದೆ.",
            "timing_conditions_en": "Early morning before heavy sun; soil should be moist but not flooded.",
            "timing_conditions_kn": "ಬೆಳಿಗ್ಗೆ ಬೇಗನೆ; ಮಣ್ಣಿನಲ್ಲಿ ಹದವಾದ ತೇವಾಂಶವಿರಬೇಕು.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": False,
            "typical_day_range": (1, 6)
        },
        {
            "stage_id": "land_prep",
            "title_en": "Apply Well-Decomposed Farmyard Manure (FYM)",
            "title_kn": "ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಕಾಂಪೋಸ್ಟ್ ಸೇರಿಸುವುದು",
            "description_en": "Incorporate 4-5 tonnes of well-rotted FYM or compost per acre into the topsoil during final puddling.",
            "description_kn": "ಕೊನೆಯ ಉಳುಮೆಯ ಸಮಯದಲ್ಲಿ ಪ್ರತಿ ಎಕರೆಗೆ 4-5 ಟನ್ ಚೆನ್ನಾಗಿ ಕಳಿತ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರವನ್ನು ಮಣ್ಣಿಗೆ ಬೆರೆಸಿ.",
            "why_necessary_en": "Supplies essential micronutrients, enhances soil microbial biodiversity, and improves cation exchange capacity.",
            "why_necessary_kn": "ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಮತ್ತು ಸೂಕ್ಷ್ಮಾಣು ಜೀವಿಗಳ ಚಟುವಟಿಕೆಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.",
            "timing_conditions_en": "Incorporate 7-10 days before transplanting.",
            "timing_conditions_kn": "ನಾಟಿಗೆ 7-10 ದಿನ ಮುಂಚಿತವಾಗಿ ಮಣ್ಣಿಗೆ ಸೇರಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "none",
            "is_recurring": False,
            "typical_day_range": (5, 12)
        },
        {
            "stage_id": "nursery",
            "title_en": "Seed Treatment with Bio-Agents",
            "title_kn": "ಜೈವಿಕ ಶಿಲೀಂಧ್ರನಾಶಕಗಳಿಂದ ಬೀಜೋಪಚಾರ",
            "description_en": "Treat selected paddy seeds with Pseudomonas fluorescens or Trichoderma harzianum @ 10g/kg seed before soaking.",
            "description_kn": "ಬಿತ್ತನೆಗೆ ಮುನ್ನ 1 ಕೆಜಿ ಭತ್ತದ ಬೀಜಕ್ಕೆ 10 ಗ್ರಾಂ ಸುಡೋಮೊನಾಸ್ ಅಥವಾ ಟ್ರೈಕೋಡರ್ಮಾದಿಂದ ಬೀಜೋಪಚಾರ ಮಾಡಿ.",
            "why_necessary_en": "Protects tender seedlings from seed-borne blast, brown spot, and bacterial leaf blight.",
            "why_necessary_kn": "ಬೆಂಕಿ ರೋಗ, ಕಂದು ಚುಕ್ಕೆ ರೋಗಗಳಿಂದ ಎಳೆಯ ಸಸಿಗಳಿಗೆ ನೈಸರ್ಗಿಕ ರಕ್ಷಣೆ ಒದಗಿಸುತ್ತದೆ.",
            "timing_conditions_en": "Treat 12-24 hours prior to incubation and sowing.",
            "timing_conditions_kn": "ನೆನೆಸುವ ಮೊದಲು ನೆರಳಿನಲ್ಲಿ ಬೀಜೋಪಚಾರ ಮಾಡಿ.",
            "priority": "high",
            "weather_sensitivity": "none",
            "is_recurring": False,
            "typical_day_range": (1, 8)
        },
        {
            "stage_id": "nursery",
            "title_en": "Raised Nursery Bed Preparation & Sowing",
            "title_kn": "ಏರು ಸಸಿಮಡಿ ಸಿದ್ಧತೆ ಮತ್ತು ಮೊಳಕೆ ಬೀಜ ಬಿತ್ತನೆ",
            "description_en": "Prepare raised nursery beds (1.5m wide with 30cm channels). Broadcast sprouted seeds uniformly and maintain moist soil without submerging.",
            "description_kn": "1.5 ಮೀ ಅಗಲದ ಏರುಮಡಿ ನಿರ್ಮಿಸಿ, ಮೊಳಕೆಯೊಡೆದ ಬೀಜಗಳನ್ನು ಸಮನಾಗಿ ಬಿತ್ತಿ. ಮಣ್ಣು ತೇವವಾಗಿರಲಿ.",
            "why_necessary_en": "Facilitates easy drainage during heavy DK coastal showers and prevents seed rot.",
            "why_necessary_kn": "ದಕ್ಷಿಣ ಕನ್ನಡದ ಭಾರಿ ಮಳೆಯ ಸಂದರ್ಭದಲ್ಲಿ ಹೆಚ್ಚುವರಿ ನೀರು ಸರಾಗವಾಗಿ ಹರಿದುಹೋಗಲು ನೆರವಾಗುತ್ತದೆ.",
            "timing_conditions_en": "Sow in calm weather, preferably late afternoon.",
            "timing_conditions_kn": "ಸಂಜೆ ತಂಪು ಹೊತ್ತಿನಲ್ಲಿ ಬಿತ್ತನೆ ಮಾಡಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": False,
            "typical_day_range": (3, 14)
        },
        {
            "stage_id": "transplanting",
            "title_en": "Paddy Field Puddling and Leveling",
            "title_kn": "ಗದ್ದೆ ಕೆಸರು ಮಾಡುವುದು ಮತ್ತು ಸಮತಟ್ಟುಗೊಳಿಸುವುದು",
            "description_en": "Puddle the field thoroughly to create an impermeable layer that reduces percolation water loss. Level smoothly.",
            "description_kn": "ನೀರು ಸೋರಿಹೋಗದಂತೆ ಗದ್ದೆಯನ್ನು ಚೆನ್ನಾಗಿ ಕೆಸರು ಮಾಡಿ, ಹಲಗೆ ಹೊಡೆದು ಸಮತಟ್ಟು ಮಾಡಿ.",
            "why_necessary_en": "Essential for uniform water depth and rapid root anchorage of young transplanted seedlings.",
            "why_necessary_kn": "ನಾಟಿ ಮಾಡಿದ ಸಸಿಗಳ ಬೇರುಗಳು ತ್ವರಿತವಾಗಿ ಮಣ್ಣಿನಲ್ಲಿ ನೆಲೆಯೂರಲು ಇದು ಅತ್ಯಗತ್ಯ.",
            "timing_conditions_en": "1-2 days before seedling transplanting.",
            "timing_conditions_kn": "ನಾಟಿಗೆ ಒಂದು ಅಥವಾ ಎರಡು ದಿನ ಮುಂಚೆ.",
            "priority": "high",
            "weather_sensitivity": "none",
            "is_recurring": False,
            "typical_day_range": (18, 26)
        },
        {
            "stage_id": "transplanting",
            "title_en": "Transplanting Healthy Seedlings at Optimal Spacing",
            "title_kn": "ಆರೋಗ್ಯಕರ ಸಸಿಗಳನ್ನು ಸೂಕ್ತ ಅಂತರದಲ್ಲಿ ನಾಟಿ ಮಾಡುವುದು",
            "description_en": "Gently pull 20-25 day old nursery seedlings. Transplant 2-3 seedlings per hill at 20x15 cm spacing at shallow depth (2-3 cm).",
            "description_kn": "20-25 ದಿನದ ಸಸಿಗಳನ್ನು 20x15 ಸೆಂ.ಮೀ ಅಂತರದಲ್ಲಿ ಪ್ರತಿ ಗುಂಪಿಗೆ 2-3 ಸಸಿಯಂತೆ ಆಳವಿಲ್ಲದೆ (2-3 ಸೆಂ.ಮೀ) ನಾಟಿ ಮಾಡಿ.",
            "why_necessary_en": "Shallow planting promotes rapid tiller emergence; optimal spacing prevents fungal overcrowding.",
            "why_necessary_kn": "ಆಳವಿಲ್ಲದ ನಾಟಿಯು ಹೆಚ್ಚು ತೆಂಡೆಗಳು ಒಡೆಯಲು ಪ್ರೇರೇಪಿಸುತ್ತದೆ.",
            "timing_conditions_en": "Avoid transplanting under scorching midday sun; cloudy days are ideal.",
            "timing_conditions_kn": "ಮೋಡ ಕವಿದ ದಿನಗಳಲ್ಲಿ ಅಥವಾ ಸಂಜೆ ವೇಳೆಯಲ್ಲಿ ನಾಟಿ ಮಾಡಿ.",
            "priority": "high",
            "weather_sensitivity": "storm_sensitive",
            "is_recurring": False,
            "typical_day_range": (20, 32)
        },
        {
            "stage_id": "vegetative",
            "title_en": "First Weeding & Cono-Weeder Operation",
            "title_kn": "ಮೊದಲ ಕಳೆ ತೆಗೆಯುವಿಕೆ / ಕೋನೋವೀಡರ್ ಚಾಲನೆ",
            "description_en": "Remove competing grassy and broadleaf weeds using a cono-weeder or manual hand weeding. Incorporate weed biomass into soil.",
            "description_kn": "ನಾಟಿ ಮಾಡಿದ 15-20 ದಿನಗಳಲ್ಲಿ ಕಳೆ ತೆಗೆಯಿರಿ. ಕಳೆಗಳನ್ನು ಮಣ್ಣಿನೊಳಗೆ ತುಳಿಯುವುದರಿಂದ ಹಸಿರೆಲೆಯಾಗಿ ಪರಿವರ್ತನೆಯಾಗುತ್ತದೆ.",
            "why_necessary_en": "Prevents severe weed-crop competition for sunlight, nitrogen, and phosphorus.",
            "why_necessary_kn": "ಬೆಳೆಗೆ ಸೂರ್ಯನ ಬೆಳಕು ಮತ್ತು ಪೋಷಕಾಂಶಗಳ ಕೊರತೆಯಾಗದಂತೆ ರಕ್ಷಿಸುತ್ತದೆ.",
            "timing_conditions_en": "Maintain 2-3 cm water level while using mechanical weeder.",
            "timing_conditions_kn": "ಗದ್ದೆಯಲ್ಲಿ ಹಿತಮಿತ ನೀರಿರುವಾಗ ಕಳೆ ತೆಗೆಯುವುದು ಸುಲಭ.",
            "priority": "high",
            "weather_sensitivity": "none",
            "is_recurring": False,
            "typical_day_range": (35, 48)
        },
        {
            "stage_id": "vegetative",
            "title_en": "First Nitrogen & Potassium Top-Dressing",
            "title_kn": "ಮೊದಲ ಮೇಲುಗೊಬ್ಬರ (ಸಾರಜನಕ ಮತ್ತು ಪೊಟ್ಯಾಷ್)",
            "description_en": "Apply the recommended split dose of Nitrogen and MOP (Muriate of Potash) in the morning when dew has evaporated.",
            "description_kn": "ಹನಿ ಒಣಗಿದ ನಂತರ ಶಿಫಾರಸು ಮಾಡಿದ ಪ್ರಮಾಣದ ಯೂರಿಯಾ ಮತ್ತು ಪೊಟ್ಯಾಷ್ ಮೇಲುಗೊಬ್ಬರವನ್ನು ನೀಡಿ.",
            "why_necessary_en": "Powers leaf chlorophyll expansion and strengthens culm resistance against lodging.",
            "why_necessary_kn": "ಎಲೆಗಳ ಹಸಿರು ಮತ್ತು ಗಿಡದ ಕಾಂಡದ ಶಕ್ತಿಯನ್ನು ವೃದ್ಧಿಸುತ್ತದೆ.",
            "timing_conditions_en": "Drain standing water to saturated mud before application; re-flood after 24 hours.",
            "timing_conditions_kn": "ಗೊಬ್ಬರ ಕೊಡುವಾಗ ಹೆಚ್ಚು ನೀರಿರಬಾರದು; ನಂತರ ನೀರು ನಿಲ್ಲಿಸಿ.",
            "priority": "medium",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": False,
            "typical_day_range": (38, 52)
        },
        {
            "stage_id": "tillering",
            "title_en": "Stem Borer & Leaf Folder Scouting",
            "title_kn": "ಕಾಂಡ ಕೊರೆಯುವ ಹುಳು ಮತ್ತು ಎಲೆ ಸುರುಳಿ ಹುಳುವಿನ ಪರಿಶೀಲನೆ",
            "description_en": "Examine 20 random hills across the plot. Check for dead hearts (drying central shoot) and longitudinal leaf folds.",
            "description_kn": "ಗದ್ದೆಯ ವಿವಿಧ ಭಾಗಗಳಲ್ಲಿ 20 ಬೆಳೆಗುಂಪುಗಳನ್ನು ಪರೀಕ್ಷಿಸಿ; ಒಣಗಿದ ಸುಳಿ ಮತ್ತು ಎಲೆ ಸುರುಳಿ ಲಕ್ಷಣಗಳನ್ನು ಗಮನಿಸಿ.",
            "why_necessary_en": "Early biological detection with Trichogramma cards or targeted bio-spray avoids economic yield loss.",
            "why_necessary_kn": "ಆರಂಭಿಕ ಹಂತದಲ್ಲೇ ಗುರುತಿಸುವುದರಿಂದ ಕೀಟ ಹಾವಳಿಯನ್ನು ಕಡಿಮೆ ವೆಚ್ಚದಲ್ಲಿ ನಿಯಂತ್ರಿಸಬಹುದು.",
            "timing_conditions_en": "Morning or late afternoon when adult moths are active.",
            "timing_conditions_kn": "ಮುಂಜಾನೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ಪರಿಶೀಲಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "none",
            "is_recurring": True,
            "typical_day_range": (50, 70)
        },
        {
            "stage_id": "panicle_initiation",
            "title_en": "Maintain 5 cm Continuous Water Level",
            "title_kn": "5 ಸೆಂ.ಮೀ ನಿರಂತರ ನೀರು ನಿರ್ವಹಣೆ",
            "description_en": "Ensure field remains submerged under 4-5 cm standing water during panicle initiation and heading.",
            "description_kn": "ತೆನೆ ಮೂಡುವ ಮತ್ತು ಹೂವಾಡುವ ಸಮಯದಲ್ಲಿ ಗದ್ದೆಯಲ್ಲಿ 4-5 ಸೆಂ.ಮೀ ನೀರು ಸತತವಾಗಿ ಇರುವಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
            "why_necessary_en": "Moisture stress at this stage causes spikelet sterility and empty chaffy grains.",
            "why_necessary_kn": "ಈ ಹಂತದಲ್ಲಿ ನೀರಿನ ಅಭಾವ ಉಂಟಾದರೆ ಜೊಳ್ಳು ಕಾಳುಗಳ ಸಂಖ್ಯೆ ಹೆಚ್ಚಾಗುತ್ತದೆ.",
            "timing_conditions_en": "Top up irrigation or adjust drainage gates according to rainfall.",
            "timing_conditions_kn": "ಮಳೆಯಿಲ್ಲದಿದ್ದರೆ ನೀರು ಹಾಯಿಸಿ, ಭಾರಿ ಮಳೆಯಾದರೆ ಬಸಿದು ನಿಯಂತ್ರಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (68, 88)
        },
        {
            "stage_id": "grain_development",
            "title_en": "Gundhi Bug & Earhead Pests Monitoring",
            "title_kn": "ಗಂಧಿ ಕೀಟ ಮತ್ತು ಕಾಳು ಕೊರೆಯುವ ಕೀಟಗಳ ನಿಗಾ",
            "description_en": "Inspect milk-stage grains in early morning hours. Look for pungent smell and sap-sucking brown adult gundhi bugs.",
            "description_kn": "ಕಾಳುಗಳಲ್ಲಿ ಹಾಲು ತುಂಬುವಾಗ ಮುಂಜಾನೆ ಗಂಧಿ ಕೀಟದ ಚಟುವಟಿಕೆ ಇದೆಯೇ ಎಂದು ಗಮನಿಸಿ.",
            "why_necessary_en": "Gundhi bug nymphs suck sweet milky sap, resulting in discolored and malformed grains.",
            "why_necessary_kn": "ಗಂಧಿ ಕೀಟವು ಹಾಲನ್ನು ಹೀರುವುದರಿಂದ ಕಾಳುಗಳು ಕಪ್ಪಾಗಿ ಜೊಳ್ಳಾಗುತ್ತವೆ.",
            "timing_conditions_en": "Before 8:30 AM when bugs rest on panicle tips.",
            "timing_conditions_kn": "ಬೆಳಿಗ್ಗೆ 8:30 ರ ಒಳಗೆ ಪರೀಕ್ಷಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "none",
            "is_recurring": True,
            "typical_day_range": (85, 105)
        },
        {
            "stage_id": "ripening",
            "title_en": "Pre-Harvest Terminal Field Drainage",
            "title_kn": "ಕೊಯ್ಲಿಗೆ ಮುನ್ನ ಗದ್ದೆಯಿಂದ ನೀರು ಬಸಿದುಬಿಡುವುದು",
            "description_en": "Open all perimeter drainage bunds to completely drain surface standing water 10-12 days before expected harvest.",
            "description_kn": "ಕೊಯ್ಲಿಗೆ 10-12 ದಿನ ಮುಂಚಿತವಾಗಿ ಗದ್ದೆಯ ಎಲ್ಲ ನೀರನ್ನು ಸಂಪೂರ್ಣವಾಗಿ ಹೊರಹಾಕಿ.",
            "why_necessary_en": "Uniform grain ripening, hardened field floor for mechanical/labour harvesting, and zero grain rotting.",
            "why_necessary_kn": "ಕಾಳುಗಳು ಸಮನಾಗಿ ಮಾಗಲು ಮತ್ತು ಕೊಯ್ಲು ಯಂತ್ರ ಅಥವಾ ಆಳುಗಳು ಗದ್ದೆಗೆ ಇಳಿಯಲು ಮಣ್ಣು ಗಟ್ಟಿಯಾಗುತ್ತದೆ.",
            "timing_conditions_en": "When 70-75% grains have turned yellow.",
            "timing_conditions_kn": "ಶೇಕಡಾ 70-75 ರಷ್ಟು ತೆನೆಗಳು ಹಳದಿ ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿದಾಗ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": False,
            "typical_day_range": (108, 122)
        },
        {
            "stage_id": "harvest",
            "title_en": "Harvesting at 85% Golden Grain Maturity",
            "title_kn": "ಸಕಾಲಿಕ ಕೊಯ್ಲು ಮತ್ತು ಬಿಸಿಲಿನಲ್ಲಿ ಒಣಗಿಸುವಿಕೆ",
            "description_en": "Harvest when 85% grains turn straw yellow. Cut stems 10-15 cm above ground, bundle, thresh, and sun-dry on clean tarpaulins.",
            "description_kn": "ಬೆಳೆ ಸರಿಯಾಗಿ ಬಲಿತಾಗ ಕೊಯ್ಲು ಮಾಡಿ, ಒಕ್ಕಣೆ ನಡೆಸಿ, ಸ್ವಚ್ಛವಾದ ತಾಡಪಾಲಿನ ಮೇಲೆ ಬಿಸಿಲಿನಲ್ಲಿ ಒಣಗಿಸಿ.",
            "why_necessary_en": "Delays cause grain shattering in the field; prompt drying to 12-14% moisture prevents mold and grain discoloration.",
            "why_necessary_kn": "ತಡಮಾಡಿದರೆ ಕಾಳುಗಳು ಉದುರುತ್ತವೆ; ಶೇ. 12-14 ತೇವಾಂಶಕ್ಕೆ ಒಣಗಿಸುವುದರಿಂದ ಶಿಲೀಂಧ್ರ ಹಿಡಿಯುವುದಿಲ್ಲ.",
            "timing_conditions_en": "On clear sunny days only; never harvest during rain showers.",
            "timing_conditions_kn": "ಬಿಸಿಲಿರುವ ಸ್ಪಷ್ಟ ದಿನಗಳಲ್ಲಿ ಮಾತ್ರ ಕೊಯ್ಲು ಮಾಡಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": False,
            "typical_day_range": (120, 135)
        }
    ],

    "Coconut": [
        {
            "stage_id": "all",
            "title_en": "Basin Irrigation & Soil Moisture Inspection",
            "title_kn": "ಬುಡಕ್ಕೆ ನೀರುಣಿಸುವಿಕೆ ಮತ್ತು ತೇವಾಂಶ ಪರಿಶೀಲನೆ",
            "description_en": "Provide 40-50 liters of water per bearing palm every 2-3 days through drip or basin during dry spells. Maintain 1.8m radius basin.",
            "description_kn": "ಮಳೆಯಿಲ್ಲದ ದಿನಗಳಲ್ಲಿ 1.8 ಮೀಟರ್ ಸುತ್ತಳತೆಯ ಬುಡಕ್ಕೆ 40-50 ಲೀಟರ್ ನೀರು ಹಾಯಿಸಿ ತೇವಾಂಶ ಕಾಪಾಡಿ.",
            "why_necessary_en": "Coconut requires consistent root zone moisture for regular inflorescence emergence and high nut retention.",
            "why_necessary_kn": "ತೇವಾಂಶದ ಕೊರತೆಯಾದರೆ ಎಳೆಯ ಕಾಯಿಗಳು (ಬಟನ್) ಉದುರುತ್ತವೆ ಮತ್ತು ಇಳುವರಿ ಕುಸಿಯುತ್ತದೆ.",
            "timing_conditions_en": "Early morning or evening; avoid midday watering.",
            "timing_conditions_kn": "ಬೆಳಿಗ್ಗೆ ಅಥವಾ ಸಂಜೆ ತಂಪು ಹೊತ್ತಿನಲ್ಲಿ ನೀರು ಹಾಯಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "all",
            "title_en": "Basin Organic Mulching with Husk and Fronds",
            "title_kn": "ತೆಂಗಿನ ಗರಿ ಮತ್ತು ಸಿಪ್ಪೆಯಿಂದ ಬುಡದ ಮಲ್ಚಿಂಗ್",
            "description_en": "Spread dry coconut leaves, husks (convex side up), or coir pith in a 2-meter radius circle around the trunk.",
            "description_kn": "ಮರದ ಬುಡದಿಂದ 2 ಮೀಟರ್ ಸುತ್ತಳತೆಯಲ್ಲಿ ಒಣ ಗರಿಗಳು ಮತ್ತು ತೆಂಗಿನ ಸಿಪ್ಪೆಯನ್ನು ಹರಡಿ ತೇವಾಂಶ ಕಾಪಾಡಿ.",
            "why_necessary_en": "Reduces soil moisture evaporation by up to 60%, cools root zone temperature, and suppresses troublesome weeds.",
            "why_necessary_kn": "ಮಣ್ಣಿನ ತೇವಾಂಶ ಆವಿಯಾಗುವುದನ್ನು ತಡೆಯುತ್ತದೆ ಮತ್ತು ಕಳೆ ಬೆಳೆಯುವುದನ್ನು ನಿಯಂತ್ರಿಸುತ್ತದೆ.",
            "timing_conditions_en": "Best carried out before the onset of summer or post-monsoon (October).",
            "timing_conditions_kn": "ಮಳೆಗಾಲದ ಕೊನೆಯಲ್ಲಿ (ಅಕ್ಟೋಬರ್) ಅಥವಾ ಬೇಸಿಗೆಗೆ ಮುಂಚೆ.",
            "priority": "medium",
            "weather_sensitivity": "none",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "all",
            "title_en": "Rhinoceros Beetle & Red Palm Weevil Crown Inspection",
            "title_kn": "ಕೊಂಬೆ ಮೂತಿ ಕೀಟ ಮತ್ತು ಕೆಂಪು ಮೂತಿ ಹುಳುವಿನ ಪರಿಶೀಲನೆ",
            "description_en": "Inspect crown for V-shaped leaf cuts (Rhinoceros beetle) and trunk for viscous oozing or chewed fibers (Red palm weevil). Fill uppermost leaf axils with neem cake and sand (1:1).",
            "description_kn": "ಗರಿಗಳಲ್ಲಿ V ಆಕಾರದ ಕಡಿತ ಮತ್ತು ಕಾಂಡದಲ್ಲಿ ಕಂದು ದ್ರವ ಜಿನುಗುವಿಕೆ ಇದೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸಿ. ಸುಳಿಯ ಸಂದಿಗಳಲ್ಲಿ ಬೇವಿನ ಹಿಂಡಿ ಮತ್ತು ಮರಳು ಮಿಶ್ರಣ ಹಾಕಿ.",
            "why_necessary_en": "Prevents lethal crown collapse caused by larval burrowing into the central growing spindle.",
            "why_necessary_kn": "ಕೀಟಗಳು ಮರದ ತಿರುಳನ್ನು ತಿಂದು ಮರ ಒಣಗಿ ಬೀಳುವುದನ್ನು ತಡೆಯುತ್ತದೆ.",
            "timing_conditions_en": "Inspect monthly, particularly during monsoon transitions.",
            "timing_conditions_kn": "ತಿಂಗಳಿಗೊಮ್ಮೆ, ಮುಖ್ಯವಾಗಿ ಮುಂಗಾರಿನ ಅವಧಿಯಲ್ಲಿ ತಪಾಸಣೆ ನಡೆಸಿ.",
            "priority": "high",
            "weather_sensitivity": "none",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "mature_bearing",
            "title_en": "Bi-Monthly Nut Harvesting & Sorting",
            "title_kn": "ದ್ವೈಮಾಸಿಕ ತೆಂಗಿನಕಾಯಿ ಕೀಳುವಿಕೆ ಮತ್ತು ವರ್ಗೀಕರಣ",
            "description_en": "Harvest mature 11-12 month old bunches using a climbing technician or telescopic pole. Lower bunches carefully in tall palms to prevent cracking.",
            "description_kn": "11-12 ತಿಂಗಳು ತುಂಬಿದ ಬಲಿತ ಕಾಯಿಗಳನ್ನು ಕೊಯ್ಲು ಮಾಡಿ. ಕಾಯಿಗಳನ್ನು ಒಡೆಯದಂತೆ ಎಚ್ಚರಿಕೆಯಿಂದ ಸಂಗ್ರಹಿಸಿ.",
            "why_necessary_en": "Harvesting on a 45-60 day schedule optimizes copra yield, oil content, and stimulates the next bunch emergence.",
            "why_necessary_kn": "ಸಕಾಲಿಕ ಕೊಯ್ಲು ಕೊಬ್ಬರಿ ಇಳುವರಿಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ ಮತ್ತು ಹೊಸ ಗೊಂಚಲುಗಳು ಹೊರಬರಲು ನೆರವಾಗುತ್ತದೆ.",
            "timing_conditions_en": "Dry, clear mornings with low wind speed for climbing safety.",
            "timing_conditions_kn": "ಗಾಳಿ ಶಾಂತವಾಗಿರುವ ಶುಷ್ಕ ಬೆಳಿಗ್ಗೆ ವೇಳೆಯಲ್ಲಿ ಕೊಯ್ಲು ನಡೆಸಿ.",
            "priority": "high",
            "weather_sensitivity": "storm_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "all",
            "title_en": "Pre-Monsoon Crown Sanitation & Bordeaux Prophylaxis",
            "title_kn": "ಮುಂಗಾರು ಪೂರ್ವ ಸುಳಿ ಸ್ವಚ್ಛತೆ ಮತ್ತು ಬೋರ್ಡೋ ಮುಲಾಮು",
            "description_en": "Clean leaf axils, remove dried inflorescence spathes and dead fibers. Apply 1% Bordeaux paste/mixture to the crown.",
            "description_kn": "ಒಣ ಗರಿ, ಹಳೆಯ ಸಿಂಗಾರಗಳನ್ನು ತೆಗೆದು ಸುಳಿಯನ್ನು ಸ್ವಚ್ಛಗೊಳಿಸಿ. ಬಡ್ ರಾಟ್ (ಸುಳಿ ಕೊಳೆ) ತಡೆಗೆ ಬೋರ್ಡೋ ದ್ರಾವಣ ಲೇಪಿಸಿ.",
            "why_necessary_en": "Dakshina Kannada's intense monsoon creates ideal humidity for Phytophthora palmivora (bud rot).",
            "why_necessary_kn": "ದಕ್ಷಿಣ ಕನ್ನಡದ ವಿಪರೀತ ಮಳೆಯಲ್ಲಿ ಸುಳಿ ಕೊಳೆ ರೋಗವು ಮರಗಳನ್ನು ಕೊಲ್ಲದಂತೆ ರಕ್ಷಣೆ ನೀಡುತ್ತದೆ.",
            "timing_conditions_en": "Complete in May before south-west monsoon rains begin.",
            "timing_conditions_kn": "ಮುಂಗಾರು ಮಳೆ ಆರಂಭವಾಗುವ ಮೊದಲು ಮೇ ತಿಂಗಳಲ್ಲಿ ಪೂರ್ಣಗೊಳಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "mature_bearing",
            "title_en": "Post-Monsoon Split Nutrient Application",
            "title_kn": "ಮುಂಗಾರು ನಂತರದ ಪೋಷಕಾಂಶ ಮತ್ತು ಗೊಬ್ಬರ ಪೂರೈಕೆ",
            "description_en": "Apply 30-40 kg well-rotted FYM + 330g Urea, 600g Rock Phosphate, and 700g Muriate of Potash per adult palm in a 1.8m ring trench; cover with soil.",
            "description_kn": "ಬುಡದಿಂದ 1.8 ಮೀ ದೂರದ ಕಾಲುವೆಯಲ್ಲಿ ಪ್ರತಿ ಮರಕ್ಕೆ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಮತ್ತು ಶಿಫಾರಸು ಮಾಡಿದ ಎನ್.ಪಿ.ಕೆ ರಸಗೊಬ್ಬರವನ್ನು ನೀಡಿ ಮಣ್ಣು ಮುಚ್ಚಿ.",
            "why_necessary_en": "Replenishes depleted reserves after heavy coastal monsoon leaching and supports flower initiation.",
            "why_necessary_kn": "ಮಳೆಯಿಂದ ಮಣ್ಣಿನ ಸತ್ವ ಕೊಚ್ಚಿಹೋಗಿರುವುದನ್ನು ಸರಿದೂಗಿಸಿ, ಮುಂದಿನ ಇಳುವರಿಯನ್ನು ಹೆಚ್ಚಿಸುತ್ತದೆ.",
            "timing_conditions_en": "September - October when soil possesses residual moisture.",
            "timing_conditions_kn": "ಸೆಪ್ಟೆಂಬರ್ - ಅಕ್ಟೋಬರ್ ತಿಂಗಳಿನಲ್ಲಿ ಮಣ್ಣಿನಲ್ಲಿ ಹದವಾದ ತೇವಾಂಶವಿರುವಾಗ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        }
    ],

    "Arecanut": [
        {
            "stage_id": "all",
            "title_en": "Drainage Channel Maintenance & De-silting",
            "title_kn": "ತೋಟದ ಚರಂಡಿ ತೋಡುವುದು ಮತ್ತು ಹೂಳೆತ್ತುವುದು",
            "description_en": "Deepen inter-row drainage trenches (60cm deep x 30cm wide) to ensure rapid rainwater evacuation from root zones.",
            "description_kn": "ಮಳೆ ನೀರು ತೋಟದಲ್ಲಿ ನಿಲ್ಲದಂತೆ ಸಾಲುಗಳ ನಡುವಿನ ಚರಂಡಿಗಳನ್ನು ಆಳವಾಗಿಸಿ (60 ಸೆಂ.ಮೀ), ಹೂಳೆತ್ತಿ ಸ್ವಚ್ಛಗೊಳಿಸಿ.",
            "why_necessary_en": "Arecanut root system is highly sensitive to waterlogging; stagnation induces root decay and yellowing.",
            "why_necessary_kn": "ಅಡಿಕೆ ಬೇರುಗಳು ನೀರು ನಿಲ್ಲುವುದನ್ನು ಸಹಿಸುವುದಿಲ್ಲ; ನೀರು ನಿಂತರೆ ಬೇರು ಕೊಳೆತು ಗರಿಗಳು ಹಳದಿಯಾಗುತ್ತವೆ.",
            "timing_conditions_en": "Prior to heavy monsoon showers (May-June) and after monsoon (October).",
            "timing_conditions_kn": "ಭಾರಿ ಮಳೆಗಾಲಕ್ಕೆ ಮುನ್ನ (ಮೇ-ಜೂನ್) ಸಿದ್ಧಪಡಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "mature_bearing",
            "title_en": "Prophylactic 1% Bordeaux Mixture Spray for Koleroga (Mahali)",
            "title_kn": "ಕೊಳೆರೋಗ (ಮಹಾಲಿ) ತಡೆಗೆ ಮುಂಜಾಗ್ರತಾ 1% ಬೋರ್ಡೋ ಸಿಂಪಡಣೆ",
            "description_en": "Spray fresh 1% neutral Bordeaux mixture with rosin soap/adherent onto all bunches before south-west monsoon onset.",
            "description_kn": "ಮುಂಗಾರು ಮಳೆ ಆರಂಭಕ್ಕೂ ಮುನ್ನ ಅಡಿಕೆ ಗೊಂಚಲುಗಳಿಗೆ 1% ಬೋರ್ಡೋ ದ್ರಾವಣವನ್ನು ಜಿಗುಟು ದ್ರವದೊಂದಿಗೆ ಚೆನ್ನಾಗಿ ಸಿಂಪಡಿಸಿ.",
            "why_necessary_en": "Koleroga (Phytophthora meadii) causes devastating premature nut drop under DK's heavy continuous monsoon downpours.",
            "why_necessary_kn": "ದಕ್ಷಿಣ ಕನ್ನಡದ ಸತತ ಮಳೆಯ ಸಮಯದಲ್ಲಿ ಅಡಿಕೆ ಕಾಯಿಗಳು ಕೊಳೆತು ಉದುರಿ ಇಡೀ ಫಸಲು ನಾಶವಾಗುವುದನ್ನು ತಡೆಯುತ್ತದೆ.",
            "timing_conditions_en": "Spray on a dry sunny morning; allow at least 4-6 hours drying before rain.",
            "timing_conditions_kn": "ಮಳೆಯಿಲ್ಲದ ಬಿಸಿಲಿನ ಬೆಳಿಗ್ಗೆ ಸಿಂಪಡಿಸಿ; ಕನಿಷ್ಠ 4-6 ಗಂಟೆ ಒಣಗಲು ಬಿಡಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "all",
            "title_en": "Basin Mulching & Summer Drip/Sprinkler Irrigation",
            "title_kn": "ಬುಡಕ್ಕೆ ಹೊದಿಕೆ (ಮಲ್ಚಿಂಗ್) ಮತ್ತು ಬೇಸಿಗೆ ನೀರಾವರಿ",
            "description_en": "Irrigate with 15-20 liters per palm daily through micro-sprinklers or drip. Mulch basins with green leaves and areca husk.",
            "description_kn": "ಬೇಸಿಗೆಯಲ್ಲಿ ಹನಿ ಅಥವಾ ತುಂತುರು ನೀರಾವರಿ ಮೂಲಕ ಮರಕ್ಕೆ ದಿನಕ್ಕೆ 15-20 ಲೀ ನೀರು ಒದಗಿಸಿ. ಬುಡಕ್ಕೆ ಅಡಿಕೆ ಸಿಪ್ಪೆಯ ಹೊದಿಕೆ ಹಾಕಿ.",
            "why_necessary_en": "Maintains optimum microclimate, prevents flower abortion, and guards young palms against sun scorching.",
            "why_necessary_kn": "ಹೂವು ಕಾಯಿ ಕಚ್ಚಲು ಅನುಕೂಲವಾಗುತ್ತದೆ ಮತ್ತು ಕಠಿಣ ಬಿಸಿಲಿನಿಂದ ಗಿಡಗಳು ಒಣಗದಂತೆ ರಕ್ಷಿಸುತ್ತದೆ.",
            "timing_conditions_en": "Operate irrigation early morning (before 9 AM) or late afternoon.",
            "timing_conditions_kn": "ಮುಂಜಾನೆ ಅಥವಾ ಸಂಜೆ ವೇಳೆ ನೀರುಣಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "mature_bearing",
            "title_en": "Second Koleroga Coverage / Polyethene Bunch Covering",
            "title_kn": "ಎರಡನೇ ಹಂತದ ಕೊಳೆರೋಗ ರಕ್ಷಣೆ / ಗೊಂಚಲಿಗೆ ಪಾಲಿಥೀನ್ ಕವಚ",
            "description_en": "Give second 1% Bordeaux spray during a monsoon break (40-45 days after 1st spray) or tie UV-stabilized polythene hoods over bunches.",
            "description_kn": "ಮೊದಲ ಸಿಂಪಡಣೆಯ 40 ದಿನಗಳ ನಂತರ ಮಳೆ ಬಿಡುವು ನೀಡಿದಾಗ ಎರಡನೇ ಸಿಂಪಡಣೆ ಮಾಡಿ ಅಥವಾ ಗೊಂಚಲುಗಳಿಗೆ ಪಾಲಿಥೀನ್ ತೊಡಿಸಿ.",
            "why_necessary_en": "Protects developing nuts from mid-monsoon fungal spore splashes without chemical residues.",
            "why_necessary_kn": "ಮಳೆಗಾಲದ ಮಧ್ಯಭಾಗದಲ್ಲಿ ಶಿಲೀಂಧ್ರ ಹರಡುವುದನ್ನು ತಡೆದು ಶೇಕಡಾ 100 ರಷ್ಟು ಕಾಯಿ ಉದುರುವುದನ್ನು ನಿಲ್ಲಿಸುತ್ತದೆ.",
            "timing_conditions_en": "During a rain break in July-August.",
            "timing_conditions_kn": "ಜುಲೈ-ಆಗಸ್ಟ್ ತಿಂಗಳಲ್ಲಿ ಮಳೆ ಬಿಡುವು ನೀಡಿದ ಸಮಯದಲ್ಲಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "mature_bearing",
            "title_en": "Nut Harvest (Tender Kalipak / Ripe Chali) & Sun-Drying",
            "title_kn": "ಅಡಿಕೆ ಕೊಯ್ಲು (ಎಳೆ ಅಡಿಕೆ / ಬಲಿತ ಚಾಲಿ) ಮತ್ತು ಒಣಗಿಸುವಿಕೆ",
            "description_en": "Harvest bunches at the correct maturity index. For Chali, harvest fully ripe yellow-orange nuts; for Kalipak, harvest tender green nuts. De-husk and sun-dry.",
            "description_kn": "ಸೂಕ್ತ ಹಂತದಲ್ಲಿ ಕೊಯ್ಲು ನಡೆಸಿ. ಚಾಲಿಗಾಗಿ ಬಲಿತ ಹಣ್ಣಡಿಕೆ ಕೊಯ್ದು, ಬಿಸಿಲಿನಲ್ಲಿ 40-45 ದಿನ ಚೆನ್ನಾಗಿ ಒಣಗಿಸಿ.",
            "why_necessary_en": "Improper drying leads to internal black mold and fungal aflatoxins, drastically reducing market price.",
            "why_necessary_kn": "ಸರಿಯಾಗಿ ಒಣಗಿಸದಿದ್ದರೆ ಕಪ್ಪು ಶಿಲೀಂಧ್ರ ಹಿಡಿದು ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಬೆಲೆ ಸಿಗುವುದಿಲ್ಲ.",
            "timing_conditions_en": "Harvest on clear dry days. Spread in clean drying yards.",
            "timing_conditions_kn": "ಬಿಸಿಲಿರುವ ಸ್ಪಷ್ಟ ದಿನಗಳಲ್ಲಿ ಒಣಗಿಸಲು ಹರಡಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        }
    ],

    "Cocoa": [
        {
            "stage_id": "all",
            "title_en": "Shade Regulation Under Arecanut/Coconut Canopy",
            "title_kn": "ತೆಂಗು/ಅಡಿಕೆ ನೆರಳಿನ ನಿಯಂತ್ರಣ (50% ಬೆಳಕು)",
            "description_en": "Prune excess upper shade branches to allow 50% diffused sunlight penetration to cocoa canopy.",
            "description_kn": "ಕೊಕ್ಕೊ ಬೆಳೆಗೆ 50% ಸೂರ್ಯನ ಬೆಳಕು ಸಿಗುವಂತೆ ಮೇಲ್ಭಾಗದ ನೆರಳನ್ನು ಸರಿಹೊಂದಿಸಿ.",
            "why_necessary_en": "Excess shade encourages fungal pod rot; excessive direct sunlight causes leaf scorching and stunted flush.",
            "why_necessary_kn": "ಹೆಚ್ಚು ನೆರಳಿದ್ದರೆ ಕೊಳೆ ರೋಗ ಬರುತ್ತದೆ; ನೇರ ಬಿಸಿಲಿದ್ದರೆ ಗರಿಗಳು ಒಣಗಿ ಇಳುವರಿ ಕಡಿಮೆಯಾಗುತ್ತದೆ.",
            "timing_conditions_en": "Post-monsoon and before peak summer (November / February).",
            "timing_conditions_kn": "ನವೆಂಬರ್ ಅಥವಾ ಫೆಬ್ರವರಿ ತಿಂಗಳಲ್ಲಿ.",
            "priority": "medium",
            "weather_sensitivity": "none",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "all",
            "title_en": "Sanitary & Structural Pruning (Chupon Removal)",
            "title_kn": "ಸಮರುವಿಕೆ ಮತ್ತು ಅನಗತ್ಯ ಕವಲುಗಳ (ಚುಪೋನ್) ತೆಗೆಯುವಿಕೆ",
            "description_en": "Cut off vertical water shoots (chupons), dead twigs, diseased branches, and parasitic plants using sharp sterilized shears.",
            "description_kn": "ಕಾಂಡದ ಮೇಲೆ ಅನಗತ್ಯವಾಗಿ ಬೆಳೆಯುವ ಜುಟ್ಟು ರೆಂಬೆಗಳು ಮತ್ತು ಒಣಗಿದ ಕೊಂಬೆಗಳನ್ನು ಕತ್ತರಿಸಿ ತೆಗೆಯಿರಿ.",
            "why_necessary_en": "Improves internal aeration, channels nutrients to flower cushions, and reduces microclimatic humidity.",
            "why_necessary_kn": "ಗಿಡದ ಒಳಭಾಗದಲ್ಲಿ ಗಾಳಿಯಾಡಲು, ಕಾಯಿಗಳಿಗೆ ಬಲ ಸಿಗಲು ಮತ್ತು ರೋಗಗಳನ್ನು ನಿಯಂತ್ರಿಸಲು ನೆರವಾಗುತ್ತದೆ.",
            "timing_conditions_en": "After major harvest rounds (August and December). Seal cut surfaces with copper paste.",
            "timing_conditions_kn": "ಕೊಯ್ಲಿನ ನಂತರ ಕತ್ತರಿಸಿ, ಕತ್ತರಿಸಿದ ಜಾಗಕ್ಕೆ ಬೋರ್ಡೋ ಮುಲಾಮು ಹಚ್ಚಿ.",
            "priority": "high",
            "weather_sensitivity": "none",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "mature_bearing",
            "title_en": "Black Pod (Phytophthora) Disease Monitoring & Prophylaxis",
            "title_kn": "ಕಪ್ಪು ಕಾಯಿ ಕೊಳೆರೋಗದ ನಿಗಾ ಮತ್ತು ಬೋರ್ಡೋ ಸಿಂಪಡಣೆ",
            "description_en": "Inspect developing pods for chocolate brown lesions. Remove and bury infected mummified pods. Spray 1% Bordeaux mixture on stems and pods.",
            "description_kn": "ಕಾಯಿಗಳ ಮೇಲೆ ಕಂದು ಮಚ್ಚೆಗಳಿವೆಯೇ ಎಂದು ಗಮನಿಸಿ. ರೋಗಪೀಡಿತ ಕಾಯಿಗಳನ್ನು ಕತ್ತರಿಸಿ ಮಣ್ಣಿನಲ್ಲಿ ಹೂಳಿ, ಬೋರ್ಡೋ ಸಿಂಪಡಿಸಿ.",
            "why_necessary_en": "Phytophthora spreads rapidly across touching pods during coastal DK humid monsoon spells.",
            "why_necessary_kn": "ದಕ್ಷಿಣ ಕನ್ನಡದ ತೇವಾಂಶಯುಕ್ತ ಮಳೆಗಾಲದಲ್ಲಿ ಕಾಯಿ ಕೊಳೆ ರೋಗವು ಇಡೀ ತೋಟಕ್ಕೆ ಹರಡುವುದನ್ನು ತಡೆಯುತ್ತದೆ.",
            "timing_conditions_en": "Monthly during rainy season from June to September.",
            "timing_conditions_kn": "ಜೂನ್‌ನಿಂದ ಸೆಪ್ಟೆಂಬರ್‌ವರೆಗೆ ಮಳೆಗಾಲದ ಅವಧಿಯಲ್ಲಿ ನಿಯಮಿತವಾಗಿ ಪರಿಶೀಲಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "mature_bearing",
            "title_en": "Ripe Pod Harvesting with Sharp Harvesting Knives",
            "title_kn": "ಬಲಿತ ಹಳದಿ/ಕಿತ್ತಳೆ ಕೊಕ್ಕೊ ಕಾಯಿಗಳ ಕೊಯ್ಲು",
            "description_en": "Harvest pods that have turned completely yellow or orange-red. Use a sharp curved knife to cut pod stalk cleanly without damaging the floral cushion.",
            "description_kn": "ಸಂಪೂರ್ಣ ಹಳದಿ ಅಥವಾ ಕಿತ್ತಳೆ ಬಣ್ಣಕ್ಕೆ ತಿರುಗಿದ ಕಾಯಿಗಳನ್ನು ಮಾತ್ರ ಹರಿತವಾದ ಚಾಕುವಿನಿಂದ ತೊಟ್ಟು ಕತ್ತರಿಸಿ ಕೊಯ್ಲು ಮಾಡಿ.",
            "why_necessary_en": "Damaging the flower cushion destroys future flowering sites permanently; unripened pods have poor cocoa bean fermentation.",
            "why_necessary_kn": "ಗಿಡದ ತೊಗಟೆಯನ್ನು ಕಿತ್ತರೆ ಮತ್ತೆ ಆ ಜಾಗದಲ್ಲಿ ಹೂವು ಅರಳುವುದಿಲ್ಲ; ಕಲಿಯದ ಕಾಯಿ ಹುದುಗುವುದಿಲ್ಲ.",
            "timing_conditions_en": "Harvest every 10-14 days during peak bearing season.",
            "timing_conditions_kn": "10-14 ದಿನಗಳಿಗೊಮ್ಮೆ ನಿಯಮಿತವಾಗಿ ಕೊಯ್ಲು ಮಾಡಿ.",
            "priority": "high",
            "weather_sensitivity": "none",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        },
        {
            "stage_id": "mature_bearing",
            "title_en": "Cocoa Bean Wooden Box Fermentation & Sun Drying",
            "title_kn": "ಕೊಕ್ಕೊ ಬೀಜಗಳ ಮರದ ಪೆಟ್ಟಿಗೆ ಹುದುಗುವಿಕೆ ಮತ್ತು ಒಣಗಿಸುವಿಕೆ",
            "description_en": "Crack pods within 2-3 days of harvest. Ferment wet beans in perforated wooden boxes for 5-6 days with turning on alternate days. Sun-dry slowly to 7% moisture.",
            "description_kn": "ಕಾಯಿಗಳನ್ನು ಒಡೆದು ಬಿಳಿ ಬೀಜಗಳನ್ನು ಮರದ ಪೆಟ್ಟಿಗೆಯಲ್ಲಿ 5-6 ದಿನ ಹುದುಗಿಸಿ, ನಂತರ ತಾಡಪಾಲಿನ ಮೇಲೆ ಬಿಸಿಲಿನಲ್ಲಿ ಒಣಗಿಸಿ.",
            "why_necessary_en": "Develops the rich chocolate flavor precursors; prevents acidic off-flavors and internal purple unfermented beans.",
            "why_necessary_kn": "ಉತ್ತಮ ಚಾಕೊಲೇಟ್ ರುಚಿ ಮತ್ತು ಪರಿಮಳ ಬರಲು ಹಾಗೂ ಉತ್ತಮ ಬೆಲೆ ಸಿಗಲು ಈ ಪ್ರಕ್ರಿಯೆ ಅತ್ಯಗತ್ಯ.",
            "timing_conditions_en": "Sun-dry on clean bamboo mats or tarpaulins for 5-7 days under bright sun.",
            "timing_conditions_kn": "ಶುದ್ಧ ಬಿಸಿಲಿನಲ್ಲಿ 5-7 ದಿನ ಸಮನಾಗಿ ಒಣಗಿಸಿ.",
            "priority": "high",
            "weather_sensitivity": "rain_sensitive",
            "is_recurring": True,
            "typical_day_range": (1, 365)
        }
    ]
}

def get_crop_stages(crop: str) -> List[Dict[str, Any]]:
    """Returns the ordered growth stages for a supported crop."""
    return CROP_STAGES.get(crop, [])

def get_default_stage_for_day(crop: str, crop_day: int) -> Dict[str, Any]:
    """Determines the default stage for a crop day based on verified agronomic rules."""
    stages = get_crop_stages(crop)
    if not stages:
        return {"id": "growth", "name_en": "Active Cultivation", "name_kn": "ಸಕ್ರಿಯ ಕೃಷಿ"}
    for stage in stages:
        if stage["start_day"] <= crop_day <= stage["end_day"]:
            return stage
    return stages[-1]

def validate_stage_consistency(crop: str, crop_day: int, selected_stage_id: str) -> Optional[str]:
    """
    Checks if a manually selected stage is consistent with the entered crop day.
    Returns a gentle warning message if inconsistent, or None if consistent.
    Does not block the user.
    """
    stages = get_crop_stages(crop)
    matching_stage = next((s for s in stages if s["id"] == selected_stage_id), None)
    if not matching_stage:
        return None
    
    start_d = matching_stage["start_day"]
    end_d = matching_stage["end_day"]
    
    # Allow some reasonable buffer (+/- 15 days or 25% flexibility)
    buffer = max(10, int(end_d * 0.2))
    if crop_day < max(1, start_d - buffer) or crop_day > (end_d + buffer):
        return (
            f"Farming Day {crop_day} is usually in the '{get_default_stage_for_day(crop, crop_day)['name_en']}' stage for {crop}. "
            f"You selected '{matching_stage['name_en']}'. If this reflects your field condition, you can proceed."
        )
    return None
