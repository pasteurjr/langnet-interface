"""
Utility functions for the application
"""
import json
import uuid
import bcrypt
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional
from jose import JWTError, jwt
from app.config import settings


def generate_uuid() -> str:
    """Generate a new UUID string"""
    return str(uuid.uuid4())


def serialize_json(data: Any) -> Optional[str]:
    """
    Serialize Python object to JSON string
    Handles datetime, date, Decimal, and other non-serializable types
    """
    if data is None:
        return None

    class CustomEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            if isinstance(obj, Decimal):
                return float(obj)
            if isinstance(obj, uuid.UUID):
                return str(obj)
            return super().default(obj)

    return json.dumps(data, cls=CustomEncoder)


def deserialize_json(json_str: Optional[str]) -> Optional[Dict]:
    """
    Deserialize JSON string to Python dict
    Returns None if input is None or invalid JSON
    """
    if not json_str:
        return None

    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None


def parse_list_field(field_value: Optional[str]) -> Optional[list]:
    """
    Parse a LONGTEXT field that stores a JSON array
    """
    if not field_value:
        return None

    if isinstance(field_value, list):
        return field_value

    try:
        parsed = json.loads(field_value)
        return parsed if isinstance(parsed, list) else None
    except (json.JSONDecodeError, TypeError):
        return None


def serialize_list_field(field_value: Optional[list]) -> Optional[str]:
    """
    Serialize a list to JSON string for storage in LONGTEXT
    """
    if field_value is None:
        return None

    if isinstance(field_value, str):
        return field_value

    return json.dumps(field_value)


# ===================================================================
# Authentication Utilities
# ===================================================================

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt
    """
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its bcrypt hash
    """
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token

    Args:
        data: Dictionary with token payload (should include user_id, email)
        expires_delta: Optional expiration time delta

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT access token

    Args:
        token: JWT token string

    Returns:
        Token payload dict if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None
