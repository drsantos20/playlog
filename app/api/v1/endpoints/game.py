from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.game import GameCreate, GameResponse, GameUpdate, GenreCreate, GenreResponse
from app.services.game_service import create_game, create_genre, get_game, update_game

router = APIRouter()

@router.post("/create", response_model=GameResponse)
async def create(game: GameCreate, db: AsyncSession = Depends(get_db)):
    game_data = await create_game(game, db)
    return game_data

@router.get("/{title}", response_model=GameResponse)
async def read(title: str, db: AsyncSession = Depends(get_db)):
    game_data = await get_game(title, db)
    if not game_data:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_data

@router.put("/{title}", response_model=GameResponse)
async def update(title: str, game: GameUpdate, db: AsyncSession = Depends(get_db)):
    game_data = await update_game(title, game, db)
    if not game_data:
        raise HTTPException(status_code=404, detail="Game not found")
    return game_data

