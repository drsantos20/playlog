from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.db.database import get_db
from app.db.models.user import User
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserResponse, UserUpdate
from app.services.user_service import authenticate_user, create_user, get_user, update_user

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login endpoint: authenticate user and return JWT token."""
    user = await authenticate_user(credentials.username, credentials.password, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    
    access_token = create_access_token(data={"sub": user.username})
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=user,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user info."""
    return current_user

@router.post("/create", response_model=UserResponse)
async def create(user: UserCreate, db: AsyncSession = Depends(get_db)):
    user_data = await create_user(user, db)
    return user_data


@router.get("/user/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    user = await get_user(username, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/update/{username}", response_model=UserResponse)
async def update(
    username: str,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user password (requires authentication)."""
    if current_user.username != username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own account",
        )
    
    updated_user = await update_user(username, user, db)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user
