from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.schemas.user_game import UserGameLogCreate, UserGameLogResponse, UserGameLogUpdate
from app.services.user_game_service import (
    delete_user_game_log,
    get_user_game_log,
    list_user_game_logs,
    log_user_game,
    update_user_game_log,
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
    user_exists, game_log = await get_user_game_log(username, title, db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    if game_log is None:
        raise HTTPException(status_code=404, detail="Game log not found")
    return game_log


@router.put("/{username}/games/{title}", response_model=UserGameLogResponse)
async def update_game_for_user(
    username: str,
    title: str,
    payload: UserGameLogUpdate,
    db: AsyncSession = Depends(get_db),
):
    user_exists, game_log = await update_user_game_log(username, title, payload, db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    if game_log is None:
        raise HTTPException(status_code=404, detail="Game log not found")
    return game_log


@router.delete("/{username}/games/{title}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game_for_user(
    username: str,
    title: str,
    db: AsyncSession = Depends(get_db),
):
    user_exists, deleted = await delete_user_game_log(username, title, db)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    if not deleted:
        raise HTTPException(status_code=404, detail="Game log not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)