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

            # Indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_saved_user ON saved_items(user_id);")
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

# Initialize DB when module is imported
init_db()
