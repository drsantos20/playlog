from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.api.v1.endpoints import user
from app.api.v1.endpoints import user_game
from app.api.v1.endpoints import game
from app.api.v1.endpoints import genre
from app.db.database import sessionmanager

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite+aiosqlite:///{BASE_DIR / 'playlog.db'}"


def init_app(init_db: bool = True):
    lifespan = None
    
    if init_db:
        sessionmanager.init(host=DATABASE_URL)
        
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            yield
            if sessionmanager._engine is not None:
                await sessionmanager.close()
                
                
    server = FastAPI(title="FastAPI with SQLAlchemy", lifespan=lifespan)
    
    server.include_router(user.router, prefix="/api/v1/users", tags=["users"])
    server.include_router(user_game.router, prefix="/api/v1/users", tags=["user-games"])
    server.include_router(game.router, prefix="/api/v1/games", tags=["games"])
    server.include_router(genre.router, prefix="/api/v1/genres", tags=["genres"])
        
    return server


app = init_app()
