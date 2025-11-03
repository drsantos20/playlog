from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import create_engine

from app.api.v1.endpoints import user
from app.api.v1.endpoints import game
from app.api.v1.endpoints import genre
from app.db.database import sessionmanager

DATABASE_URL = "sqlite+aiosqlite:///./playlog.db"
engine = create_engine(DATABASE_URL, echo=True)


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
    server.include_router(game.router, prefix="/api/v1/games", tags=["games"])
    server.include_router(genre.router, prefix="/api/v1/genres", tags=["genres"])
        
    return server
