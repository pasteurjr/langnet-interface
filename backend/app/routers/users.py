"""
Users router - CRUD endpoints for users
"""
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas import User, UserCreate, UserUpdate
from app.database import execute_query, execute_insert, execute_update, execute_delete
from app.utils import generate_uuid
from app.dependencies import get_pagination_params, validate_uuid
from passlib.context import CryptContext

router = APIRouter(prefix="/users", tags=["users"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate):
    """Create a new user"""
    user_id = generate_uuid()
    password_hash = pwd_context.hash(user.password)

    query = """
        INSERT INTO users (id, name, email, password_hash, role)
        VALUES (%s, %s, %s, %s, %s)
    """

    execute_insert(query, (user_id, user.name, user.email, password_hash, user.role))
    return get_user(user_id)


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    """Get a user by ID"""
    validate_uuid(user_id, "User ID")

    user = execute_query("SELECT * FROM users WHERE id = %s", (user_id,), fetch_one=True)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.get("/", response_model=List[User])
def list_users(pagination: dict = Depends(get_pagination_params)):
    """List all users"""
    query = "SELECT * FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s"
    return execute_query(query, (pagination['limit'], pagination['skip']), fetch_all=True)


@router.patch("/{user_id}", response_model=User)
def update_user(user_id: str, user_update: UserUpdate):
    """Update a user"""
    validate_uuid(user_id, "User ID")
    get_user(user_id)

    update_fields = []
    params = []

    for field, value in user_update.model_dump(exclude_unset=True).items():
        if field == "password":
            update_fields.append("password_hash = %s")
            params.append(pwd_context.hash(value))
        else:
            update_fields.append(f"{field} = %s")
            params.append(value)

    if not update_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")

    params.append(user_id)
    query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
    execute_update(query, tuple(params))
    return get_user(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str):
    """Delete a user"""
    validate_uuid(user_id, "User ID")
    get_user(user_id)
    execute_delete("DELETE FROM users WHERE id = %s", (user_id,))
