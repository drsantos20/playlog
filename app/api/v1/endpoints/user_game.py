from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user_game import UserGameLogCreate, UserGameLogResponse
from app.services.user_game_service import (
    get_user_game_log,
    list_user_game_logs,
    log_user_game,
)

router = APIRouter()


@router.post("/{username}/games/log", response_model=UserGameLogResponse)
async def log_game_for_user(
    username: str,
    payload: UserGameLogCreate,
    db: AsyncSession = Depends(get_db),
):
    game_log = await log_user_game(username, payload, db)
    if game_log is None:
        raise HTTPException(status_code=404, detail="User not found")
    return game_log


@router.get("/{username}/games", response_model=list[UserGameLogResponse])
async def list_games_for_user(username: str, db: AsyncSession = Depends(get_db)):
    game_logs = await list_user_game_logs(username, db)
    if game_logs is None:
        raise HTTPException(status_code=404, detail="User not found")
    return game_logs


@router.get("/{username}/games/{title}", response_model=UserGameLogResponse)
async def get_game_for_user(title: str, username: str, db: AsyncSession = Depends(get_db)):
    game_log = await get_user_game_log(username, title, db)
    if game_log is None:
        raise HTTPException(status_code=404, detail="Game log not found")
    return game_log