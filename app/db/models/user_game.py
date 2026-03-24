from datetime import date
from typing import Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class UserGame(SQLModel, table=True):
    __tablename__ = "user_games"
    __table_args__ = (
        UniqueConstraint("user_id", "game_id", name="uq_user_games_user_id_game_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    game_id: int = Field(foreign_key="games.id", index=True)
    hours_played: int
    finished_at: Optional[date] = Field(default=None)

    user: Optional["User"] = Relationship(back_populates="game_logs")
    game: Optional["Game"] = Relationship(back_populates="user_logs")