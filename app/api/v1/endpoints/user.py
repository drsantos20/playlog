from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import create_user, get_user, update_user

router = APIRouter()

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
async def update(username: str, user: UserUpdate, db: AsyncSession = Depends(get_db)):
    updated_user = await update_user(username, user, db)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    return updated_user
