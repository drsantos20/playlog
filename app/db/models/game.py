import enum

from typing import Optional

from sqlmodel import Field, Relationship, SQLModel, Enum, Column


class Game(SQLModel, table=True):
    __tablename__ = "games"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    title: str = Field(unique=True, index=True)
    genre_id: Optional[int] = Field(default=None, foreign_key="genres.id")

    genre: Optional["Genre"] = Relationship(back_populates="games")
    user_logs: list["UserGame"] = Relationship(back_populates="game")


class Genre(SQLModel, table=True):
    __tablename__ = "genres"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: str = Field(unique=True, index=True)
    description: str

    games: list["Game"] = Relationship(back_populates="genre")
    

class PlatformEnum(str, enum.Enum):
    PC = "PC"
    PS1 = "PS1"
    PS2 = "PS2"
    PS3 = "PS3"
    PS4 = "PS4"
    PS5 = "PS5"
    XBOX_ONE = "XBOX_ONE"
    XBOX_SERIES_X = "XBOX_SERIES_X"
    SWITCH = "SWITCH"
    GAME_BOY = "GAME_BOY"
    GAME_BOY_COLOR = "GAME_BOY_COLOR"
    GAME_CUBE = "GAME_CUBE"
    SNES = "SNES"
    MEGA_DRIVE = "MEGA_DRIVE"
    MASTER_SYSTEM = "MASTER_SYSTEM"


class Platform(SQLModel, table=True):
    __tablename__ = "platforms"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    name: Optional[PlatformEnum] = Field(default=None, sa_column=Column(Enum(PlatformEnum)))
    description: str
