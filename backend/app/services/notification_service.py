"""
Notification & Web Push Service.
Manages in-app notifications and scheduled weather alert delivery.
"""

import time
import logging
from typing import Dict, Any, List
from backend.app.services.firebase_service import (
    get_notification_preferences,
    get_notifications,
    _IN_MEMORY_DB,
    get_firestore_client
)

logger = logging.getLogger("kissan_guide.notifications")

# Track dispatched alerts per user to prevent duplicate spam: (uid, alert_key) -> timestamp
_DISPATCHED_ALERTS: Dict[str, float] = {}
DEDUPLICATE_WINDOW = 3600 * 6  # 6 hours

async def dispatch_weather_alert_notification(uid: str, alert: Dict[str, Any]) -> bool:
    """
    Checks user preferences and dispatches an in-app alert notification if not recently sent.
    """
    prefs = await get_notification_preferences(uid)
    category = alert.get("category", "")

    # Match category preferences
    if category == "Thunderstorm" and not prefs.get("thunderstormEnabled", True):
        return False
    if category == "Heavy Rainfall" and not prefs.get("rainfallEnabled", True):
        return False
    if category == "Heat Alert" and not prefs.get("heatEnabled", True):
        return False
    if category == "High Wind" and not prefs.get("windEnabled", True):
        return False

    # Deduplicate
    dedup_key = f"{uid}_{alert.get('category')}_{alert.get('affected_location')}"
    last_sent = _DISPATCHED_ALERTS.get(dedup_key, 0)
    now = time.time()
    if now - last_sent < DEDUPLICATE_WINDOW:
        return False

    notif_id = f"notif_alert_{int(now * 1000)}"
    notif_data = {
        "notificationId": notif_id,
        "userId": uid,
        "title_en": alert.get("title_en", "Severe Weather Advisory"),
        "title_kn": alert.get("title_kn", "ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ"),
        "message_en": f"Alert for {alert.get('affected_location')}: {alert.get('precautions_en', ['Stay safe'])[0]}",
        "message_kn": f"{alert.get('affected_location_kn')} ಭಾಗದಲ್ಲಿ ಎಚ್ಚರಿಕೆ: {alert.get('precautions_kn', ['ಸುರಕ್ಷಿತವಾಗಿರಿ'])[0]}",
        "category": alert.get("category", "Severe Weather"),
        "severity": alert.get("severity", "Severe"),
        "isRead": False,
        "createdAt": int(now),
        "source": alert.get("source", "Weather Monitor"),
    }

    client = get_firestore_client()
    if client:
        try:
            client.collection("notifications").document(notif_id).set(notif_data)
        except Exception as e:
            logger.error(f"Error saving alert notification to Firestore: {e}")

    _IN_MEMORY_DB["notifications"][notif_id] = notif_data
    _DISPATCHED_ALERTS[dedup_key] = now
    return True
