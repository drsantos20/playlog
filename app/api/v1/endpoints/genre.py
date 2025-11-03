from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.game import GenreCreate, GenreResponse
from app.services.game_service import create_genre, list_genres

router = APIRouter()


@router.post("/create", response_model=GenreResponse)
async def create(genre: GenreCreate, db: AsyncSession = Depends(get_db)):
    genre_data = await create_genre(genre, db)
    return genre_data


@router.get("/list", response_model=list[GenreResponse])
async def read_all(db: AsyncSession = Depends(get_db)):
    genres_data = await list_genres(db)
    return genres_data
