from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PlayLog"
    SECRET_KEY: str = "f4b8e7e1f7b1e8d1e8b1e8d1e8b1e8d1"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
