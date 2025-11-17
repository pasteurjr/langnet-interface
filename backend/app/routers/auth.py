"""
Authentication router - Login, Register, and user profile endpoints
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import RedirectResponse
from app.schemas import UserCreate, UserLogin, LoginResponse, User
from app.database import execute_query, execute_insert, get_db_connection
from app.utils import generate_uuid, get_password_hash, verify_password, create_access_token
from app.dependencies import get_current_user
import os

router = APIRouter(prefix="/auth", tags=["auth"])

# Google OAuth configuration (estas credenciais seriam configuradas via environment variables em produção)
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "demo-client-id")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "demo-secret")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3001")


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate):
    """
    Register a new user

    Creates a new user account with hashed password.
    """
    # Check if email already exists
    existing_user = execute_query(
        "SELECT id FROM users WHERE email = %s",
        (user_data.email,),
        fetch_one=True
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Create new user
    user_id = generate_uuid()
    password_hash = get_password_hash(user_data.password)

    query = """
        INSERT INTO users (id, name, email, password_hash, role, is_active)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    execute_insert(
        query,
        (user_id, user_data.name, user_data.email, password_hash,
         user_data.role or 'user', True)
    )

    # Fetch and return the created user
    created_user = execute_query(
        """SELECT id, name, email, role, is_active, created_at, updated_at, last_login
           FROM users WHERE id = %s""",
        (user_id,),
        fetch_one=True
    )

    return created_user


@router.post("/login", response_model=LoginResponse)
def login(credentials: UserLogin):
    """
    Login endpoint

    Authenticates user and returns JWT access token.
    """
    # Find user by email
    user = execute_query(
        "SELECT * FROM users WHERE email = %s",
        (credentials.email,),
        fetch_one=True
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user['is_active']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Update last_login timestamp
    with get_db_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.utcnow(), user['id'])
        )
        connection.commit()
        cursor.close()

    # Create access token
    token_data = {
        "user_id": user['id'],
        "email": user['email']
    }
    access_token = create_access_token(token_data)

    # Prepare user response (without password_hash)
    user_response = {
        "id": user['id'],
        "name": user['name'],
        "email": user['email'],
        "role": user.get('role'),
        "is_active": user['is_active'],
        "created_at": user['created_at'],
        "updated_at": user['updated_at'],
        "last_login": datetime.utcnow()
    }

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }


@router.get("/me", response_model=User)
def get_current_user_profile(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user profile

    Returns the profile of the currently logged-in user based on JWT token.
    """
    return current_user


@router.get("/google/login")
def google_login():
    """
    Initiate Google OAuth login flow

    Redirects user to Google's OAuth consent screen.
    """
    # Build Google OAuth URL
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
        "&access_type=offline"
        "&prompt=consent"
    )

    return RedirectResponse(url=google_auth_url)


@router.get("/google/callback")
async def google_callback(code: str = None, error: str = None):
    """
    Google OAuth callback endpoint

    Handles the OAuth callback from Google and creates/logs in the user.
    """
    if error:
        # Redirect to frontend with error
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error={error}")

    if not code:
        return RedirectResponse(url=f"{FRONTEND_URL}/login?error=no_code")

    try:
        # Em produção, aqui você trocaria o code por um access_token usando a API do Google
        # Por ora, vamos criar um usuário de demonstração

        # NOTA: Em produção, você faria:
        # 1. Trocar o code pelo access_token com Google
        # 2. Usar o access_token para buscar dados do usuário (email, name, picture)
        # 3. Criar ou buscar usuário no banco
        # 4. Gerar JWT token

        # Simulação para demonstração:
        demo_user_email = f"google_user_{code[:8]}@gmail.com"
        demo_user_name = "Google User"

        # Check if user exists
        user = execute_query(
            "SELECT * FROM users WHERE email = %s",
            (demo_user_email,),
            fetch_one=True
        )

        # If user doesn't exist, create it
        if not user:
            user_id = generate_uuid()
            execute_insert(
                """INSERT INTO users
                (id, name, email, password_hash, role, is_active, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (
                    user_id,
                    demo_user_name,
                    demo_user_email,
                    get_password_hash("oauth_user"),  # senha placeholder
                    'user',
                    True,
                    datetime.utcnow(),
                    datetime.utcnow()
                )
            )

            user = execute_query(
                "SELECT * FROM users WHERE id = %s",
                (user_id,),
                fetch_one=True
            )

        # Update last login
        execute_insert(
            "UPDATE users SET last_login = %s WHERE id = %s",
            (datetime.utcnow(), user['id'])
        )

        # Generate JWT token
        token_data = {
            'user_id': user['id'],
            'email': user['email']
        }
        access_token = create_access_token(token_data)

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?token={access_token}&name={user['name']}"
        )

    except Exception as e:
        print(f"Google OAuth error: {e}")
        return RedirectResponse(
            url=f"{FRONTEND_URL}/login?error=oauth_failed"
        )
