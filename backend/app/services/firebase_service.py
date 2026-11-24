"""
Firebase Firestore & Storage Service with automatic resilient fallback.
Handles users, recommendations, storage records, bookmarks, and notifications.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional
from backend.app.core.config import settings
from backend.app.services.database import (
    save_item_db,
    get_saved_items_db,
    delete_saved_item_db
)

logger = logging.getLogger("kissan_guide.firebase")

# In-memory store for development/testing when Firestore credentials are not mounted
_IN_MEMORY_DB: Dict[str, Dict[str, Dict[str, Any]]] = {
    "users": {},
    "crop_recommendations": {},
    "storage_records": {},
    "saved_items": {},
    "notifications": {},
    "notification_preferences": {},
}

def get_firestore_client():
    if not (settings.FIREBASE_CREDENTIALS_PATH and os.path.exists(settings.FIREBASE_CREDENTIALS_PATH)):
        return None
    try:
        import firebase_admin
        from firebase_admin import firestore
        if firebase_admin._apps:
            return firestore.client()
    except Exception as e:
        logger.debug(f"Firestore client uninitialized or error: {e}")
    return None

# ==================== User Profile ====================

async def get_user_profile(uid: str) -> Optional[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            doc = client.collection("users").document(uid).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.error(f"Firestore get_user error: {e}")
    
    # Fallback store
    if uid in _IN_MEMORY_DB["users"]:
        return _IN_MEMORY_DB["users"][uid]
    
    # Default profile for fresh UID
    default_profile = {
        "uid": uid,
        "fullName": "Farmer",
        "email": "",
        "phoneNumber": "",
        "taluk": "Mangaluru",
        "district": "Dakshina Kannada",
        "state": "Karnataka",
        "preferredLanguage": "en",
        "primaryCrops": ["Coconut", "Arecanut"],
        "farmingExperienceYears": 5,
        "profilePicture": None,
        "createdAt": int(time.time()),
        "updatedAt": int(time.time()),
    }
    _IN_MEMORY_DB["users"][uid] = default_profile
    return default_profile

async def update_user_profile(uid: str, data: Dict[str, Any]) -> Dict[str, Any]:
    data["updatedAt"] = int(time.time())
    client = get_firestore_client()
    if client:
        try:
            client.collection("users").document(uid).set(data, merge=True)
            doc = client.collection("users").document(uid).get()
            return doc.to_dict()
        except Exception as e:
            logger.error(f"Firestore update_user error: {e}")
    
    existing = await get_user_profile(uid)
    existing.update(data)
    _IN_MEMORY_DB["users"][uid] = existing
    return existing

async def delete_user_account(uid: str) -> bool:
    client = get_firestore_client()
    if client:
        try:
            client.collection("users").document(uid).delete()
        except Exception as e:
            logger.error(f"Firestore delete_user error: {e}")
    
    _IN_MEMORY_DB["users"].pop(uid, None)
    return True

# ==================== Saved / Bookmarks ====================

async def save_item(uid: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
    saved_id = item_data.get("savedItemId") or f"save_{int(time.time() * 1000)}"
    item_data["savedItemId"] = saved_id
    item_data["userId"] = uid
    item_data["createdAt"] = item_data.get("createdAt") or int(time.time())

    client = get_firestore_client()
    if client:
        try:
            client.collection("saved_items").document(saved_id).set(item_data)
            return item_data
        except Exception as e:
            logger.error(f"Firestore save_item error: {e}")

    # Fallback to persistent SQLite database
    try:
        return save_item_db(uid, item_data)
    except Exception as e:
        logger.debug(f"SQLite save_item error: {e}")
        _IN_MEMORY_DB["saved_items"][saved_id] = item_data
        return item_data

async def get_saved_items(uid: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            query = client.collection("saved_items").where("userId", "==", uid)
            if category:
                query = query.where("itemType", "==", category)
            docs = query.stream()
            return [d.to_dict() for d in docs]
        except Exception as e:
            logger.error(f"Firestore get_saved_items error: {e}")

    # Fallback to persistent SQLite database
    try:
        db_items = get_saved_items_db(uid)
        if category:
            db_items = [item for item in db_items if item.get("itemType") == category]
        return db_items
    except Exception as e:
        logger.debug(f"SQLite get_saved_items error: {e}")

    # Memory Fallback

async def delete_saved_item(uid: str, saved_item_id: str) -> bool:
    client = get_firestore_client()
    if client:
        try:
            client.collection("saved_items").document(saved_item_id).delete()
            return True
        except Exception as e:
            logger.error(f"Firestore delete_saved_item error: {e}")

    # SQLite fallback
    try:
        deleted = delete_saved_item_db(uid, saved_item_id)
        if deleted:
            return True
    except Exception as e:
        logger.debug(f"SQLite delete_saved_item error: {e}")

    if saved_item_id in _IN_MEMORY_DB["saved_items"]:
        del _IN_MEMORY_DB["saved_items"][saved_item_id]
        return True
    return False

# ==================== Storage Records ====================

async def save_storage_record(uid: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
    storage_id = record_data.get("storageId") or f"storage_{int(time.time() * 1000)}"
    record_data["storageId"] = storage_id
    record_data["userId"] = uid
    record_data["createdAt"] = int(time.time())

    client = get_firestore_client()
    if client:
        try:
            client.collection("storage_records").document(storage_id).set(record_data)
            return record_data
        except Exception as e:
            logger.error(f"Firestore save_storage_record error: {e}")

    _IN_MEMORY_DB["storage_records"][storage_id] = record_data
    return record_data

async def get_storage_records(uid: str) -> List[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            docs = client.collection("storage_records").where("userId", "==", uid).stream()
            return [d.to_dict() for d in docs]
        except Exception as e:
            logger.error(f"Firestore get_storage_records error: {e}")

    records = [
        r for r in _IN_MEMORY_DB["storage_records"].values()
        if r.get("userId") == uid
    ]
    records.sort(key=lambda x: x.get("createdAt", 0), reverse=True)
    return records

# ==================== Crop Recommendation History ====================

async def save_crop_recommendation(uid: str, rec_data: Dict[str, Any]) -> Dict[str, Any]:
    rec_id = rec_data.get("recommendationId") or f"rec_{int(time.time() * 1000)}"
    rec_data["recommendationId"] = rec_id
    rec_data["userId"] = uid
    rec_data["createdAt"] = int(time.time())

    client = get_firestore_client()
    if client:
        try:
            client.collection("crop_recommendations").document(rec_id).set(rec_data)
            return rec_data
        except Exception as e:
            logger.error(f"Firestore save_crop_rec error: {e}")

    _IN_MEMORY_DB["crop_recommendations"][rec_id] = rec_data
    return rec_data

async def get_crop_recommendations(uid: str) -> List[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            docs = client.collection("crop_recommendations").where("userId", "==", uid).stream()
            return [d.to_dict() for d in docs]
        except Exception as e:
            logger.error(f"Firestore get_crop_recommendations error: {e}")

    records = [
        r for r in _IN_MEMORY_DB["crop_recommendations"].values()
        if r.get("userId") == uid
    ]
    records.sort(key=lambda x: x.get("createdAt", 0), reverse=True)
    return records

# ==================== Notifications & Preferences ====================

async def get_notifications(uid: str) -> List[Dict[str, Any]]:
    client = get_firestore_client()
    if client:
        try:
            docs = client.collection("notifications").where("userId", "==", uid).stream()
            return [d.to_dict() for d in docs]
        except Exception as e:
            logger.error(f"Firestore get_notifications error: {e}")

    # Fallback: check or seed with welcome notification
    user_notifs = [n for n in _IN_MEMORY_DB["notifications"].values() if n.get("userId") == uid]
    if not user_notifs:
        welcome_notif = {
            "notificationId": f"notif_welcome_{uid}",
            "userId": uid,
            "title_en": "Welcome to KISSAN GUIDE!",
            "title_kn": "ಕಿಸಾನ್ ಗೈಡ್‌ಗೆ ಸ್ವಾಗತ!",
            "message_en": "Your Dakshina Kannada smart farming advisory is ready. Explore crop recommendations, weather alerts, and storage guidelines.",
            "message_kn": "ದಕ್ಷಿಣ ಕನ್ನಡದ ರೈತರಿಗಾಗಿ ನಿಮ್ಮ ಕೃಷಿ ಮಾರ್ಗದರ್ಶಿ ಸಿದ್ಧವಾಗಿದೆ. ಬೆಳೆ ಶಿಫಾರಸು, ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ಹಾಗೂ ಸಂಗ್ರಹಣಾ ಸಲಹೆಗಳನ್ನು ಪಡೆದುಕೊಳ್ಳಿ.",
            "category": "General Advisory",
            "severity": "Informational",
            "isRead": False,
            "createdAt": int(time.time()),
        }
        _IN_MEMORY_DB["notifications"][welcome_notif["notificationId"]] = welcome_notif
        user_notifs.append(welcome_notif)

    user_notifs.sort(key=lambda x: x.get("createdAt", 0), reverse=True)
    return user_notifs

async def mark_notification_read(uid: str, notification_id: str) -> bool:
    client = get_firestore_client()
    if client:
        try:
            client.collection("notifications").document(notification_id).update({"isRead": True})
            return True
        except Exception as e:
            logger.error(f"Firestore mark_read error: {e}")

    if notification_id in _IN_MEMORY_DB["notifications"]:
        _IN_MEMORY_DB["notifications"][notification_id]["isRead"] = True
        return True
    return False

async def get_notification_preferences(uid: str) -> Dict[str, Any]:
    client = get_firestore_client()
    if client:
        try:
            doc = client.collection("notification_preferences").document(uid).get()
            if doc.exists:
                return doc.to_dict()
        except Exception as e:
            logger.error(f"Firestore get_pref error: {e}")

    if uid in _IN_MEMORY_DB["notification_preferences"]:
        return _IN_MEMORY_DB["notification_preferences"][uid]

    defaults = {
        "userId": uid,
        "thunderstormEnabled": True,
        "rainfallEnabled": True,
        "heatEnabled": True,
        "windEnabled": True,
        "generalAdvisoryEnabled": True,
        "pushEnabled": False,
    }
    _IN_MEMORY_DB["notification_preferences"][uid] = defaults
    return defaults

async def update_notification_preferences(uid: str, prefs: Dict[str, Any]) -> Dict[str, Any]:
    prefs["userId"] = uid
    client = get_firestore_client()
    if client:
        try:
            client.collection("notification_preferences").document(uid).set(prefs, merge=True)
            return prefs
        except Exception as e:
            logger.error(f"Firestore update_pref error: {e}")

    _IN_MEMORY_DB["notification_preferences"][uid] = prefs
    return prefs
