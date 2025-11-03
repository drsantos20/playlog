from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from app.db.models.game import Game, Genre
from app.schemas.game import GameCreate, GenreCreate


async def create_game(game: GameCreate, db: AsyncSession):
    genre_exists = await db.execute(
        select(Genre).where(Genre.id == game.genre_id)
    )
    genre_exists = genre_exists.scalars().first()
    if not genre_exists:
        raise  HTTPException(status_code=400, detail="Invalid genre_id")


    save_game = Game(
        title=game.title,
        genre_id=game.genre_id
    )
    db.add(save_game)
    await db.commit()
    await db.refresh(save_game)

    load_game = (
        select(Game)
            .where(Game.title == game.title)
            .options(selectinload(Game.genre))
    )

    result = await db.execute(load_game)
    game_result = result.scalars().first()
    return game_result


async def get_game(title: str, db: AsyncSession):
    find_game = await db.execute(
        select(Game).where(Game.title == title).options(selectinload(Game.genre))
    )
    fetched_game = find_game.scalars().first()
    return fetched_game


async def update_game(title: str, game: GameCreate, db: AsyncSession):
    find_game = await db.execute(
        select(Game).where(Game.title == title)
    )
    game_to_update = find_game.scalars().first()

    if game_to_update:
        game_to_update.title = game.title
        game_to_update.genre_id = game.genre_id

        await db.commit()
        await db.refresh(game_to_update)
        
        # Load the updated game with genre relationship
        updated_game = await db.execute(
            select(Game).where(Game.title == game.title).options(selectinload(Game.genre))
        )
        return updated_game.scalars().first()
    return None


async def create_genre(genre: GenreCreate, db: AsyncSession):
    new_genre = Genre(
        name=genre.name,
        description=genre.description
    )
    db.add(new_genre)
    await db.commit()
    await db.refresh(new_genre)
    return new_genre


async def list_genres(db: AsyncSession):
    genres = await db.execute(select(Genre))
    return genres.scalars().all()
