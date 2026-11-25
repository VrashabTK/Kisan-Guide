import os
import re
import time
import json
import uuid
import secrets
import sqlite3
import logging
from typing import Optional, Dict, Any, Tuple, List
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
import jwt

from backend.app.core.config import settings

logger = logging.getLogger("kissan_guide.database")

# Argon2id password hasher instance
ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=1,
    hash_len=32
)

# Supported crops for Dakshina Kannada
VALID_CROPS = {"Coconut", "Rice", "Arecanut", "Cocoa"}

def get_db_connection() -> sqlite3.Connection:
    """Creates a connection to SQLite database with WAL mode enabled."""
    db_path = settings.SQLITE_DB_PATH
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn

def init_db():
    """Initializes tables and indexes for users, authentication, and user data."""
    conn = get_db_connection()
    try:
        with conn:
            # Users table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE,
                phone_number TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                full_name TEXT,
                taluk TEXT DEFAULT 'Mangaluru',
                district TEXT DEFAULT 'Dakshina Kannada',
                state TEXT DEFAULT 'Karnataka',
                preferred_language TEXT DEFAULT 'en',
                selected_crop TEXT DEFAULT 'Arecanut',
                primary_crops TEXT DEFAULT '["Coconut", "Arecanut"]',
                farming_experience_years INTEGER DEFAULT 5,
                profile_picture TEXT,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            );
            """)

            # Rate limiting / Brute force attempts table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS login_attempts (
                identifier TEXT PRIMARY KEY,
                failed_count INTEGER DEFAULT 0,
                last_attempt INTEGER DEFAULT 0,
                locked_until INTEGER DEFAULT 0
            );
            """)

            # Password reset tokens table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS password_resets (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                identifier TEXT NOT NULL,
                expires_at INTEGER NOT NULL,
                used INTEGER DEFAULT 0
            );
            """)

            # Saved items table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS saved_items (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                item_type TEXT NOT NULL,
                item_id TEXT NOT NULL,
                title TEXT NOT NULL,
                title_kn TEXT,
                crop TEXT,
                location TEXT,
                content TEXT NOT NULL,
                created_at INTEGER NOT NULL
            );
            """)

            # Storage records table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS storage_records (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                crop TEXT NOT NULL,
                data TEXT NOT NULL,
                created_at INTEGER NOT NULL
            );
            """)

            # Farms table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS farms (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                name TEXT,
                crop TEXT NOT NULL,
                taluk TEXT NOT NULL,
                area REAL NOT NULL,
                area_unit TEXT DEFAULT 'acre',
                cultivation_start_date TEXT,
                initial_farming_day INTEGER DEFAULT 1,
                monitoring_start_date TEXT NOT NULL,
                current_stage TEXT NOT NULL,
                variety TEXT,
                cultivation_method TEXT,
                soil_type TEXT,
                water_availability TEXT DEFAULT 'Moderate',
                notes TEXT,
                is_active INTEGER DEFAULT 1,
                created_at INTEGER NOT NULL,
                updated_at INTEGER NOT NULL
            );
            """)

            # Farm activities table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS farm_activities (
                id TEXT PRIMARY KEY,
                farm_id TEXT NOT NULL,
                calendar_date TEXT NOT NULL,
                crop_day INTEGER NOT NULL,
                monitoring_day INTEGER NOT NULL,
                stage TEXT NOT NULL,
                title_en TEXT NOT NULL,
                title_kn TEXT NOT NULL,
                description_en TEXT NOT NULL,
                description_kn TEXT NOT NULL,
                why_necessary_en TEXT NOT NULL,
                why_necessary_kn TEXT NOT NULL,
                timing_conditions_en TEXT,
                timing_conditions_kn TEXT,
                priority TEXT DEFAULT 'medium',
                weather_influence_en TEXT,
                weather_influence_kn TEXT,
                status TEXT DEFAULT 'pending',
                completed_at INTEGER,
                skipped_at INTEGER,
                skip_reason TEXT,
                is_recurring INTEGER DEFAULT 0,
                created_at INTEGER NOT NULL
            );
            """)

            # Farm observations table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS farm_observations (
                id TEXT PRIMARY KEY,
                farm_id TEXT NOT NULL,
                calendar_date TEXT NOT NULL,
                crop_day INTEGER NOT NULL,
                monitoring_day INTEGER NOT NULL,
                field_condition TEXT,
                soil_moisture TEXT,
                water_availability TEXT,
                crop_appearance TEXT,
                pest_symptoms TEXT,
                rainfall_notes TEXT,
                additional_notes TEXT,
                photo_url TEXT,
                created_at INTEGER NOT NULL
            );
            """)

            # Farm progress corrections table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS farm_corrections (
                id TEXT PRIMARY KEY,
                farm_id TEXT NOT NULL,
                prev_crop_day INTEGER,
                new_crop_day INTEGER,
                prev_stage TEXT,
                new_stage TEXT,
                reason TEXT,
                created_at INTEGER NOT NULL
            );
            """)

            # Farm harvests table
            conn.execute("""
            CREATE TABLE IF NOT EXISTS farm_harvests (
                id TEXT PRIMARY KEY,
                farm_id TEXT NOT NULL,
                harvest_date TEXT NOT NULL,
                quantity_kg REAL NOT NULL,
                quality_grade TEXT,
                storage_method TEXT,
                notes TEXT,
                created_at INTEGER NOT NULL
            );
            """)

            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_saved_user ON saved_items(user_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_farms_user ON farms(user_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_farm ON farm_activities(farm_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_activities_date ON farm_activities(farm_id, calendar_date);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_obs_farm ON farm_observations(farm_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_harvest_farm ON farm_harvests(farm_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_storage_user ON storage_records(user_id);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_resets_token ON password_resets(token);")
            
        logger.info(f"SQLite database initialized at {settings.SQLITE_DB_PATH}")
    finally:
        conn.close()

# Normalization & Validation Functions
def normalize_identifier(identifier: str) -> Tuple[str, str]:
    """
    Determines if identifier is an email or Indian mobile number, validates, and normalizes it.
    Returns: (type: 'email' | 'phone', normalized_value: str)
    Raises ValueError if invalid.
    """
    raw = (identifier or "").strip()
    if not raw:
        raise ValueError("Identifier cannot be empty")

    if "@" in raw:
        email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        normalized = raw.lower()
        if not re.match(email_regex, normalized):
            raise ValueError("Please enter a valid email address.")
        return "email", normalized
    else:
        # Mobile number normalization
        digits = re.sub(r"\D", "", raw)
        if digits.startswith("91") and len(digits) == 12:
            digits = digits[2:]
        elif digits.startswith("0") and len(digits) == 11:
            digits = digits[1:]

        if len(digits) != 10:
            raise ValueError("Please enter a valid 10-digit Indian mobile number.")
        if digits[0] not in "6789":
            raise ValueError("Indian mobile numbers must start with 6, 7, 8, or 9.")

        normalized = f"+91{digits}"
        return "phone", normalized

def hash_password(password: str) -> str:
    """Hashes a password using Argon2id."""
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long.")
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against an Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, VerificationError, Exception):
        return False

# JWT Token Functions
def create_access_token(user_id: str, email: Optional[str] = None, phone: Optional[str] = None, name: Optional[str] = None) -> str:
    """Generates a secure HS256 JWT access token."""
    now = int(time.time())
    expire = now + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60)
    payload = {
        "sub": user_id,
        "uid": user_id,
        "email": email or "",
        "phone_number": phone or "",
        "name": name or "Farmer",
        "iat": now,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates a JWT access token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except Exception as e:
        logger.debug(f"JWT decode error: {e}")
        return None

# User Database Operations
def user_row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Converts a database row into a public farmer profile dict (never leaking password_hash)."""
    if not row:
        return {}
    
    primary_crops = ["Coconut", "Arecanut"]
    if row["primary_crops"]:
        try:
            primary_crops = json.loads(row["primary_crops"])
        except Exception:
            pass

    return {
        "uid": row["id"],
        "id": row["id"],
        "email": row["email"] or "",
        "phoneNumber": row["phone_number"] or "",
        "fullName": row["full_name"] or "Farmer",
        "taluk": row["taluk"] or "Mangaluru",
        "district": row["district"] or "Dakshina Kannada",
        "state": row["state"] or "Karnataka",
        "preferredLanguage": row["preferred_language"] or "en",
        "selected_crop": row["selected_crop"] or "Arecanut",
        "selectedCrop": row["selected_crop"] or "Arecanut",
        "primaryCrops": primary_crops,
        "farmingExperienceYears": row["farming_experience_years"] or 5,
        "profilePicture": row["profile_picture"],
        "createdAt": row["created_at"],
        "updatedAt": row["updated_at"],
    }

def check_account_exists(email: Optional[str] = None, phone_number: Optional[str] = None) -> bool:
    """Checks whether an account with the given email or phone already exists."""
    conn = get_db_connection()
    try:
        if email and phone_number:
            cur = conn.execute("SELECT id FROM users WHERE email = ? OR phone_number = ? LIMIT 1;", (email, phone_number))
        elif email:
            cur = conn.execute("SELECT id FROM users WHERE email = ? LIMIT 1;", (email,))
        elif phone_number:
            cur = conn.execute("SELECT id FROM users WHERE phone_number = ? LIMIT 1;", (phone_number,))
        else:
            return False
        return cur.fetchone() is not None
    finally:
        conn.close()

def create_user(
    identifier: str,
    password: str,
    full_name: Optional[str] = None,
    taluk: str = "Mangaluru"
) -> Dict[str, Any]:
    """
    Registers a new user with email OR phone number.
    Atomically ensures no duplicates exist.
    Hashes password with Argon2id.
    Returns user profile dict and access token.
    """
    id_type, normalized = normalize_identifier(identifier)
    email = normalized if id_type == "email" else None
    phone_number = normalized if id_type == "phone" else None

    # Step 1: Check existence
    if check_account_exists(email=email, phone_number=phone_number):
        raise ValueError("An account with this email address or mobile number already exists. Please log in.")

    # Step 2: Hash password
    hashed = hash_password(password)

    user_id = f"usr_{uuid.uuid4().hex[:12]}"
    now = int(time.time())
    display_name = (full_name or "").strip() or ("Farmer" if not email else email.split("@")[0].capitalize())

    conn = get_db_connection()
    try:
        # Atomic transaction to guarantee no simultaneous signup collisions
        with conn:
            conn.execute("""
            INSERT INTO users (
                id, email, phone_number, password_hash, full_name,
                taluk, district, state, preferred_language, selected_crop,
                primary_crops, farming_experience_years, profile_picture,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                user_id,
                email,
                phone_number,
                hashed,
                display_name,
                taluk,
                "Dakshina Kannada",
                "Karnataka",
                "en",
                "Arecanut",
                json.dumps(["Coconut", "Arecanut"]),
                5,
                None,
                now,
                now
            ))
            
            cur = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
            user_row = cur.fetchone()
            profile = user_row_to_dict(user_row)

        token = create_access_token(user_id=user_id, email=email, phone=phone_number, name=display_name)
        return {
            "user": profile,
            "access_token": token,
            "token_type": "bearer"
        }
    except sqlite3.IntegrityError:
        raise ValueError("An account with this email address or mobile number already exists. Please log in.")
    finally:
        conn.close()

# Rate Limiting & Brute Force Protection
def check_rate_limit(identifier: str) -> Tuple[bool, int]:
    """
    Checks if identifier is rate-limited (too many failed attempts).
    Returns (is_allowed: bool, retry_after_seconds: int)
    """
    now = int(time.time())
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM login_attempts WHERE identifier = ?;", (identifier,))
        row = cur.fetchone()
        if not row:
            return True, 0

        locked_until = row["locked_until"]
        if locked_until > now:
            return False, locked_until - now

        # If last attempt was more than 15 mins ago, reset failed count
        if now - row["last_attempt"] > 900:
            with conn:
                conn.execute("DELETE FROM login_attempts WHERE identifier = ?;", (identifier,))
            return True, 0

        return True, 0
    finally:
        conn.close()

def record_failed_login(identifier: str):
    """Increments failed login attempts. Locks out after 5 consecutive failures."""
    now = int(time.time())
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute("SELECT * FROM login_attempts WHERE identifier = ?;", (identifier,))
            row = cur.fetchone()
            if row:
                count = row["failed_count"] + 1
                locked_until = (now + 900) if count >= 5 else 0
                conn.execute("""
                UPDATE login_attempts
                SET failed_count = ?, last_attempt = ?, locked_until = ?
                WHERE identifier = ?;
                """, (count, now, locked_until, identifier))
            else:
                conn.execute("""
                INSERT INTO login_attempts (identifier, failed_count, last_attempt, locked_until)
                VALUES (?, 1, ?, 0);
                """, (identifier, now))
    finally:
        conn.close()

def clear_failed_login(identifier: str):
    """Resets failed login attempts upon successful login."""
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("DELETE FROM login_attempts WHERE identifier = ?;", (identifier,))
    finally:
        conn.close()

def authenticate_user(identifier: str, password: str) -> Dict[str, Any]:
    """
    Authenticates a user with email OR phone number + password.
    Returns user profile dict and token.
    Raises ValueError with generic message if authentication fails.
    """
    try:
        _, normalized = normalize_identifier(identifier)
    except ValueError:
        # Invalid format -> raise generic invalid credentials
        raise ValueError("Invalid credentials. Please check your email/mobile number and password.")

    # Rate limit check
    allowed, retry_after = check_rate_limit(normalized)
    if not allowed:
        raise ValueError(f"Too many failed login attempts. Please wait {retry_after} seconds before trying again.")

    conn = get_db_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM users WHERE email = ? OR phone_number = ? LIMIT 1;",
            (normalized, normalized)
        )
        user_row = cur.fetchone()

        if not user_row:
            record_failed_login(normalized)
            raise ValueError("Invalid credentials. Please check your email/mobile number and password.")

        # Verify password
        if not verify_password(password, user_row["password_hash"]):
            record_failed_login(normalized)
            raise ValueError("Invalid credentials. Please check your email/mobile number and password.")

        # Successful login: clear brute-force counters
        clear_failed_login(normalized)

        profile = user_row_to_dict(user_row)
        token = create_access_token(
            user_id=profile["uid"],
            email=profile.get("email"),
            phone=profile.get("phoneNumber"),
            name=profile.get("fullName")
        )
        return {
            "user": profile,
            "access_token": token,
            "token_type": "bearer"
        }
    finally:
        conn.close()

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Retrieves a user profile by unique ID."""
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
        row = cur.fetchone()
        return user_row_to_dict(row) if row else None
    finally:
        conn.close()

def update_user_profile(user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """Updates user profile fields and persists to SQLite."""
    allowed_keys = {
        "fullName": "full_name",
        "taluk": "taluk",
        "district": "district",
        "state": "state",
        "preferredLanguage": "preferred_language",
        "selected_crop": "selected_crop",
        "selectedCrop": "selected_crop",
        "farmingExperienceYears": "farming_experience_years",
        "profilePicture": "profile_picture",
    }

    set_clauses = []
    values = []
    now = int(time.time())

    for k, v in updates.items():
        if k in allowed_keys and v is not None:
            db_col = allowed_keys[k]
            # Validate selected_crop
            if db_col == "selected_crop":
                if v not in VALID_CROPS:
                    continue
            set_clauses.append(f"{db_col} = ?")
            values.append(v)
        elif k == "primaryCrops" and isinstance(v, list):
            set_clauses.append("primary_crops = ?")
            values.append(json.dumps([c for c in v if c in VALID_CROPS]))

    set_clauses.append("updated_at = ?")
    values.append(now)
    values.append(user_id)

    conn = get_db_connection()
    try:
        with conn:
            conn.execute(
                f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?;",
                tuple(values)
            )
            cur = conn.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
            row = cur.fetchone()
            return user_row_to_dict(row)
    finally:
        conn.close()

def update_crop_preference(user_id: str, crop: str) -> Dict[str, Any]:
    """Updates the shared crop selection for a user."""
    if crop not in VALID_CROPS:
        raise ValueError(f"Crop must be one of {list(VALID_CROPS)}")
    return update_user_profile(user_id, {"selected_crop": crop})

# Forgot Password / Reset Flow
def create_password_reset_token(identifier: str) -> Dict[str, Any]:
    """
    Creates a password reset request.
    Verifies that the account actually exists before issuing a token.
    Raises ValueError if account does not exist.
    """
    _, normalized = normalize_identifier(identifier)
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "SELECT id, email, phone_number FROM users WHERE email = ? OR phone_number = ? LIMIT 1;",
            (normalized, normalized)
        )
        user = cur.fetchone()
        if not user:
            raise ValueError("No account found with this email address or mobile number.")

        token = secrets.token_hex(16)
        now = int(time.time())
        expires_at = now + 900  # 15 minutes validity

        with conn:
            conn.execute("""
            INSERT INTO password_resets (token, user_id, identifier, expires_at, used)
            VALUES (?, ?, ?, ?, 0);
            """, (token, user["id"], normalized, expires_at))

        return {
            "token": token,
            "identifier": normalized,
            "expires_in_seconds": 900,
            "message": "Password reset token generated successfully."
        }
    finally:
        conn.close()

def reset_password(token: str, new_password: str) -> bool:
    """Validates reset token and sets new password."""
    if len(new_password) < 6:
        raise ValueError("Password must be at least 6 characters long.")

    now = int(time.time())
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute(
                "SELECT * FROM password_resets WHERE token = ? AND used = 0 AND expires_at > ?;",
                (token, now)
            )
            reset_row = cur.fetchone()
            if not reset_row:
                raise ValueError("Invalid or expired password reset token.")

            user_id = reset_row["user_id"]
            new_hash = hash_password(new_password)

            conn.execute(
                "UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?;",
                (new_hash, now, user_id)
            )
            conn.execute(
                "UPDATE password_resets SET used = 1 WHERE token = ?;",
                (token,)
            )
            return True
    finally:
        conn.close()

# Saved Items Operations
def save_item_db(user_id: str, item_data: Dict[str, Any]) -> Dict[str, Any]:
    now = int(time.time())
    saved_id = item_data.get("savedItemId") or item_data.get("id") or f"save_{uuid.uuid4().hex[:10]}"
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT OR REPLACE INTO saved_items (id, user_id, item_type, item_id, title, title_kn, crop, location, content, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                saved_id,
                user_id,
                item_data.get("itemType", "General"),
                item_data.get("itemId", saved_id),
                item_data.get("title", "Saved Item"),
                item_data.get("title_kn"),
                item_data.get("crop"),
                item_data.get("location"),
                json.dumps(item_data.get("content", {})),
                now
            ))
            return {**item_data, "id": saved_id, "savedItemId": saved_id, "userId": user_id, "createdAt": now}
    finally:
        conn.close()

def get_saved_items_db(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.execute("SELECT * FROM saved_items WHERE user_id = ? ORDER BY created_at DESC;", (user_id,))
        rows = cur.fetchall()
        items = []
        for r in rows:
            try:
                content = json.loads(r["content"])
            except Exception:
                content = {}
            items.append({
                "id": r["id"],
                "savedItemId": r["id"],
                "userId": r["user_id"],
                "itemType": r["item_type"],
                "itemId": r["item_id"],
                "title": r["title"],
                "title_kn": r["title_kn"],
                "crop": r["crop"],
                "location": r["location"],
                "content": content,
                "createdAt": r["created_at"]
            })
        return items
    finally:
        conn.close()

def delete_saved_item_db(user_id: str, item_id: str) -> bool:
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute("DELETE FROM saved_items WHERE (id = ? OR item_id = ?) AND user_id = ?;", (item_id, item_id, user_id))
            return cur.rowcount > 0
    finally:
        conn.close()

# ==================== Farm Management Database Operations ====================

def create_farm_db(farm_data: Dict[str, Any]) -> Dict[str, Any]:
    farm_id = farm_data.get("id") or f"farm_{uuid.uuid4().hex[:12]}"
    now = int(time.time())
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO farms (
                id, user_id, name, crop, taluk, area, area_unit,
                cultivation_start_date, initial_farming_day, monitoring_start_date,
                current_stage, variety, cultivation_method, soil_type,
                water_availability, notes, is_active, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                farm_id,
                farm_data["user_id"],
                farm_data.get("name") or f"{farm_data['crop']} Farm ({farm_data['taluk']})",
                farm_data["crop"],
                farm_data["taluk"],
                float(farm_data["area"]),
                farm_data.get("area_unit", "acre"),
                farm_data.get("cultivation_start_date"),
                int(farm_data.get("initial_farming_day", 1)),
                farm_data["monitoring_start_date"],
                farm_data["current_stage"],
                farm_data.get("variety"),
                farm_data.get("cultivation_method"),
                farm_data.get("soil_type"),
                farm_data.get("water_availability", "Moderate"),
                farm_data.get("notes"),
                1,
                now,
                now
            ))
        return get_farm_by_id_db(farm_id, farm_data["user_id"])
    finally:
        conn.close()

def get_farms_by_user_db(user_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM farms WHERE user_id = ? AND is_active = 1 ORDER BY created_at DESC;",
            (user_id,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def get_farm_by_id_db(farm_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        if user_id:
            cur = conn.execute("SELECT * FROM farms WHERE id = ? AND user_id = ?;", (farm_id, user_id))
        else:
            cur = conn.execute("SELECT * FROM farms WHERE id = ?;", (farm_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()

def update_farm_db(farm_id: str, user_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    now = int(time.time())
    allowed_keys = {
        "name", "crop", "taluk", "area", "area_unit", "cultivation_start_date",
        "initial_farming_day", "current_stage", "variety", "cultivation_method",
        "soil_type", "water_availability", "notes"
    }
    filtered = {k: v for k, v in updates.items() if k in allowed_keys and v is not None}
    if not filtered:
        return get_farm_by_id_db(farm_id, user_id)
    
    set_clauses = [f"{k} = ?" for k in filtered.keys()]
    set_clauses.append("updated_at = ?")
    values = list(filtered.values()) + [now, farm_id, user_id]

    try:
        with conn:
            conn.execute(
                f"UPDATE farms SET {', '.join(set_clauses)} WHERE id = ? AND user_id = ?;",
                values
            )
        return get_farm_by_id_db(farm_id, user_id)
    finally:
        conn.close()

def delete_farm_db(farm_id: str, user_id: str) -> bool:
    conn = get_db_connection()
    try:
        with conn:
            cur = conn.execute(
                "UPDATE farms SET is_active = 0, updated_at = ? WHERE id = ? AND user_id = ?;",
                (int(time.time()), farm_id, user_id)
            )
            return cur.rowcount > 0
    finally:
        conn.close()

def create_farm_correction_db(correction: Dict[str, Any]) -> Dict[str, Any]:
    cid = correction.get("id") or f"corr_{uuid.uuid4().hex[:12]}"
    now = int(time.time())
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO farm_corrections (
                id, farm_id, prev_crop_day, new_crop_day, prev_stage, new_stage, reason, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                cid,
                correction["farm_id"],
                correction.get("prev_crop_day"),
                correction.get("new_crop_day"),
                correction.get("prev_stage"),
                correction.get("new_stage"),
                correction.get("reason"),
                now
            ))
            # Also update farm current_stage / initial_farming_day if provided
            farm_updates = {}
            if "new_stage" in correction and correction["new_stage"]:
                farm_updates["current_stage"] = correction["new_stage"]
            if "new_crop_day" in correction and correction["new_crop_day"]:
                farm_updates["initial_farming_day"] = correction["new_crop_day"]
                # Reset monitoring_start_date to today so day calculation stays aligned
                from datetime import date
                farm_updates["monitoring_start_date"] = date.today().isoformat()
            if farm_updates:
                set_clauses = [f"{k} = ?" for k in farm_updates.keys()]
                set_clauses.append("updated_at = ?")
                vals = list(farm_updates.values()) + [now, correction["farm_id"]]
                conn.execute(f"UPDATE farms SET {', '.join(set_clauses)} WHERE id = ?;", vals)

        return {**correction, "id": cid, "created_at": now}
    finally:
        conn.close()

def get_farm_corrections_db(farm_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM farm_corrections WHERE farm_id = ? ORDER BY created_at DESC;",
            (farm_id,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def save_farm_activities_db(activities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    saved = []
    now = int(time.time())
    try:
        with conn:
            for act in activities:
                aid = act.get("id") or f"act_{uuid.uuid4().hex[:12]}"
                conn.execute("""
                INSERT OR REPLACE INTO farm_activities (
                    id, farm_id, calendar_date, crop_day, monitoring_day, stage,
                    title_en, title_kn, description_en, description_kn,
                    why_necessary_en, why_necessary_kn, timing_conditions_en, timing_conditions_kn,
                    priority, weather_influence_en, weather_influence_kn,
                    status, completed_at, skipped_at, skip_reason, is_recurring, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """, (
                    aid,
                    act["farm_id"],
                    act["calendar_date"],
                    int(act["crop_day"]),
                    int(act["monitoring_day"]),
                    act["stage"],
                    act["title_en"],
                    act["title_kn"],
                    act["description_en"],
                    act["description_kn"],
                    act["why_necessary_en"],
                    act["why_necessary_kn"],
                    act.get("timing_conditions_en"),
                    act.get("timing_conditions_kn"),
                    act.get("priority", "medium"),
                    act.get("weather_influence_en"),
                    act.get("weather_influence_kn"),
                    act.get("status", "pending"),
                    act.get("completed_at"),
                    act.get("skipped_at"),
                    act.get("skip_reason"),
                    1 if act.get("is_recurring") else 0,
                    act.get("created_at", now)
                ))
                saved.append({**act, "id": aid})
        return saved
    finally:
        conn.close()

def get_farm_activities_for_date_db(farm_id: str, calendar_date: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM farm_activities WHERE farm_id = ? AND calendar_date = ? ORDER BY created_at ASC;",
            (farm_id, calendar_date)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def get_farm_activities_history_db(farm_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM farm_activities WHERE farm_id = ? ORDER BY calendar_date DESC, created_at DESC LIMIT ?;",
            (farm_id, limit)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def update_farm_activity_status_db(
    activity_id: str,
    farm_id: str,
    status: str,
    skip_reason: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    now = int(time.time())
    completed_at = now if status == "completed" else None
    skipped_at = now if status == "skipped" else None
    try:
        with conn:
            conn.execute("""
            UPDATE farm_activities
            SET status = ?, completed_at = ?, skipped_at = ?, skip_reason = ?
            WHERE id = ? AND farm_id = ?;
            """, (status, completed_at, skipped_at, skip_reason, activity_id, farm_id))
            cur = conn.execute("SELECT * FROM farm_activities WHERE id = ?;", (activity_id,))
            row = cur.fetchone()
            return dict(row) if row else None
    finally:
        conn.close()

def create_farm_observation_db(obs_data: Dict[str, Any]) -> Dict[str, Any]:
    oid = obs_data.get("id") or f"obs_{uuid.uuid4().hex[:12]}"
    now = int(time.time())
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO farm_observations (
                id, farm_id, calendar_date, crop_day, monitoring_day,
                field_condition, soil_moisture, water_availability,
                crop_appearance, pest_symptoms, rainfall_notes,
                additional_notes, photo_url, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                oid,
                obs_data["farm_id"],
                obs_data["calendar_date"],
                int(obs_data["crop_day"]),
                int(obs_data["monitoring_day"]),
                obs_data.get("field_condition"),
                obs_data.get("soil_moisture"),
                obs_data.get("water_availability"),
                obs_data.get("crop_appearance"),
                obs_data.get("pest_symptoms"),
                obs_data.get("rainfall_notes"),
                obs_data.get("additional_notes"),
                obs_data.get("photo_url"),
                now
            ))
        return {**obs_data, "id": oid, "created_at": now}
    finally:
        conn.close()

def get_farm_observations_db(farm_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM farm_observations WHERE farm_id = ? ORDER BY calendar_date DESC, created_at DESC LIMIT ?;",
            (farm_id, limit)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

def create_farm_harvest_db(harvest_data: Dict[str, Any]) -> Dict[str, Any]:
    hid = harvest_data.get("id") or f"harv_{uuid.uuid4().hex[:12]}"
    now = int(time.time())
    conn = get_db_connection()
    try:
        with conn:
            conn.execute("""
            INSERT INTO farm_harvests (
                id, farm_id, harvest_date, quantity_kg, quality_grade, storage_method, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (
                hid,
                harvest_data["farm_id"],
                harvest_data["harvest_date"],
                float(harvest_data["quantity_kg"]),
                harvest_data.get("quality_grade", "Grade A"),
                harvest_data.get("storage_method"),
                harvest_data.get("notes"),
                now
            ))
        return {**harvest_data, "id": hid, "created_at": now}
    finally:
        conn.close()

def get_farm_harvests_db(farm_id: str) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        cur = conn.execute(
            "SELECT * FROM farm_harvests WHERE farm_id = ? ORDER BY harvest_date DESC, created_at DESC;",
            (farm_id,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()

# Initialize DB when module is imported
init_db()
