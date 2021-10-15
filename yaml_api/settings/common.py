import os

from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = False
    APP_NAME: str = "Ymal API"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "DEBUG"
    LOG_FORMAT: str = (
        "{level} {time:YYYY-MM-DD HH:mm:ss} {name}:{function}-{message} | {extra}"
    )


class MongoSettings(BaseSettings):
    uri: AnyUrl
    db: str

    class Config:
        env_prefix = "mongo_"
        env_file_encoding = "utf8"
        env_file = os.getenv("MONGO_ENV_FILE", "./.env.local")
        extra = "ignore"


class RedisSettings(BaseSettings):
    uri: AnyUrl

    class Config:
        env_prefix = "redis_"
        env_file_encoding = "utf8"
        env_file = os.getenv("REDIS_ENV_FILE", "./.env.local")
        extra = "ignore"


class Neo4jSettings(BaseSettings):
    url: AnyUrl
    user: str
    password: str

    class Config:
        env_prefix = "NEO4J_"
        env_file_encoding = "utf8"
        env_file = os.getenv("NEO4J_ENV_FILE", "./.env.local")
        extra = "ignore"


settings = Settings()
mongo_settings = MongoSettings()
redis_settings = RedisSettings()
neo4j_settings = Neo4jSettings()

# For convinience
DEBUG = settings.DEBUG
APP_NAME = settings.APP_NAME
APP_VERSION = settings.APP_VERSION

RUN_LEVEL = os.getenv("RUN_LEVEL", "dev")
