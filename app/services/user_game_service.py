from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.db.models.game import Game, Genre
from app.db.models.user import User
from app.db.models.user_game import UserGame
from app.schemas.user_game import UserGameLogCreate, UserGameLogUpdate


async def _get_user(username: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def _get_or_create_genre(genre_data, db: AsyncSession):
    if genre_data is None:
        return None

    result = await db.execute(select(Genre).where(Genre.name == genre_data.name))
    genre = result.scalars().first()
    if genre is not None:
        return genre

    genre = Genre(name=genre_data.name, description=genre_data.description)
    db.add(genre)
    await db.flush()
    return genre


async def _load_user_game(log_id: int, db: AsyncSession):
    result = await db.execute(
        select(UserGame)
        .where(UserGame.id == log_id)
        .options(
            selectinload(UserGame.game).selectinload(Game.genre),
        )
    )
    return result.scalars().first()


async def log_user_game(username: str, payload: UserGameLogCreate, db: AsyncSession):
    user = await _get_user(username, db)
    if user is None:
        return None

    result = await db.execute(
        select(Game).where(Game.title == payload.title).options(selectinload(Game.genre))
    )
    game = result.scalars().first()
    genre = await _get_or_create_genre(payload.genre, db)

    if game is None:
        game = Game(
            title=payload.title,
            genre_id=genre.id if genre is not None else None,
        )
        db.add(game)
        await db.flush()
    elif game.genre_id is None and genre is not None:
        game.genre_id = genre.id
        await db.flush()

    result = await db.execute(
        select(UserGame).where(
            UserGame.user_id == user.id,
            UserGame.game_id == game.id,
        )
    )
    user_game = result.scalars().first()

    if user_game is None:
        user_game = UserGame(
            user_id=user.id,
            game_id=game.id,
            hours_played=payload.hours_played,
            finished_at=payload.finished_at,
        )
        db.add(user_game)
    else:
        user_game.hours_played = payload.hours_played
        user_game.finished_at = payload.finished_at

    await db.flush()
    log_id = user_game.id
    await db.commit()
    return await _load_user_game(log_id, db)


async def list_user_game_logs(username: str, db: AsyncSession):
    user = await _get_user(username, db)
    if user is None:
        return None

    result = await db.execute(
        select(UserGame)
        .where(UserGame.user_id == user.id)
        .options(selectinload(UserGame.game).selectinload(Game.genre))
        .order_by(UserGame.id)
    )
    return result.scalars().all()


async def get_user_game_log(username: str, title: str, db: AsyncSession):
    user = await _get_user(username, db)
    if user is None:
        return False, None

    result = await db.execute(
        select(UserGame)
        .join(Game)
        .where(UserGame.user_id == user.id, Game.title == title)
        .options(selectinload(UserGame.game).selectinload(Game.genre))
    )
    return True, result.scalars().first()


async def update_user_game_log(
    username: str,
    title: str,
    payload: UserGameLogUpdate,
    db: AsyncSession,
):
    user_exists, game_log = await get_user_game_log(username, title, db)
    if not user_exists:
        return False, None
    if game_log is None:
        return True, None

    game_log.hours_played = payload.hours_played
    game_log.finished_at = payload.finished_at
    log_id = game_log.id

    await db.commit()
    updated_log = await _load_user_game(log_id, db)
    return True, updated_log


async def delete_user_game_log(username: str, title: str, db: AsyncSession):
    user_exists, game_log = await get_user_game_log(username, title, db)
    if not user_exists:
        return False, False
    if game_log is None:
        return True, False

    await db.delete(game_log)
    await db.commit()
    return True, True