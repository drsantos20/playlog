from pydantic import BaseModel, ConfigDict


class GameBase(BaseModel):
    title: str
    genre_id: int
    

class GameCreate(GameBase):
    pass


class GameUpdate(GameBase):
    pass


class GameResponse(GameBase):
    id: int
    genre: str
    title: str
    genre_id: int
    class Config:
        orm_mode = True


class GenreBase(BaseModel):
    name: str
    description: str
    

class GenreCreate(GenreBase):
    pass


class GenreUpdate(GenreBase):
    pass


class GenreResponse(GenreBase):
    id: int
    name: str
    description: str
    class Config:
        orm_mode = True


class PlatformBase(BaseModel):
    name: str
    description: str


class PlatformCreate(PlatformBase):
    pass


class PlatformUpdate(PlatformBase):
    pass


class PlatformResponse(PlatformBase):
    id: int
    name: str
    description: str
    class Config:
        orm_mode = True


model_config = ConfigDict(str_max_length=50)
