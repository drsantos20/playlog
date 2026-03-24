from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.game import GenreCreate, GenreResponse


class UserGameLogCreate(BaseModel):
    title: str
    hours_played: int = Field(ge=0)
    finished_at: Optional[date] = None
    genre: Optional[GenreCreate] = None


class UserGameLogGameResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    genre: Optional[GenreResponse] = None


class UserGameLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    hours_played: int
    finished_at: Optional[date] = None
    game: UserGameLogGameResponse