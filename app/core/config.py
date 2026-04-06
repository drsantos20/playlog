from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "PlayLog"
    SECRET_KEY: str = "f4b8e7e1f7b1e8d1e8b1e8d1e8b1e8d1"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"


settings = Settings()
