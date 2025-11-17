"""
FastAPI dependencies
"""
from typing import Optional
from fastapi import HTTPException, status, Query, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.utils import decode_access_token
from app.database import get_db_connection

security = HTTPBearer()


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return")
) -> dict:
    """
    Get pagination parameters
    """
    return {"skip": skip, "limit": limit}


def validate_uuid(uuid_str: str, field_name: str = "ID") -> str:
    """
    Validate UUID format
    Raises HTTPException if invalid
    """
    import uuid
    try:
        uuid.UUID(uuid_str)
        return uuid_str
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {field_name} format. Must be a valid UUID."
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Get current user from JWT token
    Validates the token and returns user information
    """
    token = credentials.credentials

    # Decode and validate token
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    email = payload.get("email")

    if not user_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify user exists in database
    with get_db_connection() as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, name, email, role, is_active, created_at, updated_at, last_login FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()
        cursor.close()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user['is_active']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return user


def get_current_user_id(current_user: dict = Depends(get_current_user)) -> str:
    """
    Get current user ID from authenticated user
    """
    return current_user['id']
